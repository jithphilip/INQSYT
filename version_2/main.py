import json
import os
from typing import TypedDict

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph

from retrieval import (
    get_candidate_chunks,
    rerank_chunks,
    retrieve_chunks,
    retrieve_intents,
)


GROQ_MODEL = "llama-3.3-70b-versatile"


class ChatState(TypedDict):
    question: str
    chat_history: list
    retrieved_intents: list
    finalized_intents: list
    intent_confidence: float
    handoff_required: bool
    retrieved_chunks: list
    context: str
    answer: str


load_dotenv()
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def intent_node(state):
    results = retrieve_intents(
        state["question"],
        k=5
    )

    state["retrieved_intents"] = results
    state["intent_confidence"] = results[0]["score"]
    return state


def intent_finalization_node(state):
    query = state["question"]
    retrieved_intents = state["retrieved_intents"]

    intent_options = []
    for item in retrieved_intents:
        intent = item["intent"]
        intent_options.append(
            {
                "intent": intent["intent"],
                "description": intent["description"],
                "sample_queries": intent["sample_queries"],
                "retrieval_score": item["score"],
            }
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an intent selection assistant. Select the 1, 2, or 3 best "
                "matching intents for the user's question from the provided "
                "candidate intents. Use the intent descriptions and sample "
                "queries. Return only valid JSON with this schema: "
                "{\"selected_intents\": [\"intent_name\"], \"reason\": \"short reason\"}."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "question": query,
                    "candidate_intents": intent_options,
                },
                indent=2,
            ),
        },
    ]

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )

    try:
        result = json.loads(
            response.choices[0].message.content
        )
        selected_names = result.get(
            "selected_intents",
            []
        )[:3]
    except json.JSONDecodeError:
        selected_names = []

    selected = [
        item
        for item in retrieved_intents
        if item["intent"]["intent"] in selected_names
    ]

    if not selected:
        selected = retrieved_intents[:1]

    state["finalized_intents"] = selected
    state["intent_confidence"] = selected[0]["score"]
    return state


def route_after_intent(state):
    intents = state.get(
        "finalized_intents",
        state["retrieved_intents"]
    )

    if not intents:
        return "human_handoff"

    if len(intents) >= 3:
        score1 = intents[0]["score"]
        score2 = intents[1]["score"]
        score3 = intents[2]["score"]
        if score1 < -5 and score2 < -5 and score3 < -5:
            return "human_handoff"
    elif len(intents) == 2:
        score1 = intents[0]["score"]
        score2 = intents[1]["score"]
        if score1 < -5 and score2 < -5:
            return "human_handoff"
    elif len(intents) == 1:
        score = intents[0]["score"]
        if score < -5:
            return "human_handoff"

    return "chunk_retrieval"


def human_handoff_node(state):
    state["answer"] = (
        "I couldn't confidently determine the best resolution for your request. "
        "Please wait while we connect your request to our support team."
    )
    state["handoff_required"] = True
    return state


def chunk_node(state):
    query = state["question"]
    candidate_ids = get_candidate_chunks(
        state.get(
            "finalized_intents",
            state["retrieved_intents"]
        )
    )
    chunks = retrieve_chunks(
        query,
        candidate_ids,
        top_k=15
    )
    reranked_chunks = rerank_chunks(
        query,
        chunks,
        top_k=5
    )
    state["retrieved_chunks"] = reranked_chunks
    return state

def route_after_chunk_retrieval(state):
    chunks = state.get(
        "retrieved_chunks",
        []
    )

    if not chunks:
        return "human_handoff"

    (
        (chunk, retrieval_score),
        rerank_score
    ) = chunks[0]

    if rerank_score < -5:
        return "human_handoff"
    return "context_builder"



def context_node(state):
    contexts = []

    for (
        (chunk, retrieval_score),
        rerank_score
    ) in state["retrieved_chunks"]:

        contexts.append(
            chunk["content"]
        )

    state["context"] = "\n\n".join(
        contexts
    )
    return state


def generation_node(state):
    history = state["chat_history"]
    context = state["context"]
    query = state["question"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful support assistant. Answer the user's question "
                "using only the provided context. If the context does not contain "
                "enough information, say that you do not have enough information, "
                "and a human agent will be in touch with the user to solve their issue. "
                "You do not have to explicitly mention that the context does not "
                "provide enough information; you can say that you do not have enough "
                "info to help the user. "
                "Some previous assistant messages may include handoff status notes; "
                "use those notes to avoid treating escalated issues as resolved."
            ),
        }
    ]

    for h in history:
        content = h["content"]
        if h["role"] == "assistant" and h.get("handoff_required") is True:
            content = (
                "[Previous assistant response was escalated to a human support agent]\n"
                + content
            )

        messages.append(
            {
                "role": h["role"],
                "content": content,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"Question:\n{query}"
            ),
        }
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.2,
    )

    state["handoff_required"] = False
    state["answer"] = response.choices[0].message.content
    return state


def memory_node(state):
    state["chat_history"].append(
        {
            "role": "user",
            "content": state["question"],
        }
    )
    state["chat_history"].append(
        {
            "role": "assistant",
            "content": state["answer"],
            "handoff_required": state.get(
                "handoff_required",
                False
            )
        }
    )
    return state


# @st.cache_resource
def build_graph():  
    graph = StateGraph(ChatState)

    graph.add_node(
        "intent_retrieval/intent_classifier",
        intent_node
    )
    graph.add_node(
        "intent_finalization",
        intent_finalization_node
    )
    graph.add_node(
        "human_handoff",
        human_handoff_node
    )
    graph.add_node(
        "chunk_retrieval",
        chunk_node
    )
    graph.add_node(
        "context_builder",
        context_node
    )
    graph.add_node(
        "generation",
        generation_node
    )
    graph.add_node(
        "memory_update",
        memory_node
    )

    graph.set_entry_point(
        "intent_retrieval/intent_classifier"
    )
    graph.add_edge(
        "intent_retrieval/intent_classifier",
        "intent_finalization"
    )
    graph.add_conditional_edges(
        "intent_finalization",
        route_after_intent,
        {
            "chunk_retrieval": "chunk_retrieval",
            "human_handoff": "human_handoff",
        },
    )
    graph.add_edge(
        "human_handoff",
        "memory_update"
    )
    
    
    graph.add_conditional_edges(
    "chunk_retrieval",
    route_after_chunk_retrieval,
    {
        "context_builder": "context_builder",
        "human_handoff": "human_handoff",
    },)
    
    
    graph.add_edge(
        "context_builder",
        "generation"
    )
    graph.add_edge(
        "generation",
        "memory_update"
    )

    return graph.compile()


def make_initial_state(question):
    return {
        "question": question,
        "chat_history": st.session_state.chat_history,
        "retrieved_intents": [],
        "finalized_intents": [],
        "intent_confidence": 0.0,
        "handoff_required": False,
        "retrieved_chunks": [],
        "context": "",
        "answer": "",
    }




#####################---------  StreamLit ----------#########################################

st.set_page_config(
    page_title="LangGraph RAG Bot",
    page_icon="",
    layout="centered",
)

st.title("LangGraph RAG Bot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not os.getenv("GROQ_API_KEY"):
    st.error("GROQ_API_KEY is missing. Add it to your .env file before chatting.")
    st.stop()

with st.sidebar:
    st.caption("Memory is kept only for this Streamlit session.")
    if st.button("Reset conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("handoff_required"):
            st.caption("Human handoff requested")

import pandas as pd
import textwrap


def render_debug_history():

    with st.expander(
        "Debug History",
        expanded=False
    ):

        for idx, debug in enumerate(
            st.session_state.debug_history,
            start=1
        ):

            st.markdown(
                f"## Query {idx}"
            )

            st.write(
                f"Question: {debug['question']}"
            )

            st.write(
                f"Handoff: {debug['handoff_required']}"
            )

            st.divider()

            # Retrieved intents
            st.subheader(
                "Retrieved Intents"
            )

            intent_rows = []

            for item in debug[
                "retrieved_intents"
            ]:

                intent_rows.append(
                    {
                        "intent":
                            item["intent"]["intent"],
                        "score":
                            round(
                                item["score"],
                                4
                            ),
                         "description":item["intent"]["description"]
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    intent_rows
                ),
                use_container_width=True,
                hide_index=True
            )

            # Final intents
            st.subheader(
                "Finalized Intents"
            )

            final_rows = []

            for item in debug[
                "finalized_intents"
            ]:

                final_rows.append(
                    {
                        "intent":
                            item["intent"]["intent"],
                        "score":
                            round(
                                item["score"],
                                4
                            ),
                         "description": item["intent"]["description"]
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    final_rows
                ),
                use_container_width=True,
                hide_index=True
            )

            # Chunks
            st.subheader(
                "Retrieved Chunks"
            )

            chunk_rows = []

            for rank, item in enumerate(
                debug["retrieved_chunks"],
                start=1
            ):

                (
                    (
                        chunk,
                        retrieval_score
                    ),
                    rerank_score
                ) = item

                chunk_rows.append(
                    {
                        "rank": rank,
                        "chunk_id":
                            chunk["chunk_id"],
                        "retrieval_score":
                            round(
                                float(
                                    retrieval_score
                                ),
                                4
                            ),
                        "rerank_score":
                            round(
                                float(
                                    rerank_score
                                ),
                                4
                            ),
                        "preview": chunk["content"][:400]
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    chunk_rows
                ),
                use_container_width=True,
                hide_index=True
            )

            st.divider()


prompt = st.chat_input("Ask a support question")



    
    
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    app = build_graph()

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = app.invoke(
                make_initial_state(prompt)
            )
        if "debug_history" not in st.session_state:
            st.session_state.debug_history = [] 
        st.session_state.debug_history.append(
    {
        "question": prompt,
        "retrieved_intents": result.get(
            "retrieved_intents",
            []
        ),
        "finalized_intents": result.get(
            "finalized_intents",
            []
        ),
        "retrieved_chunks": result.get(
            "retrieved_chunks",
            []
        ),
        "answer": result.get(
            "answer",
            ""
        ),
        "handoff_required": result.get(
            "handoff_required",
            False
        )
    }
)

        st.markdown(
                result["answer"]
            )

        if result.get(
            "handoff_required"
        ):
            st.caption(
                "Human handoff requested"
            )
        

        st.write("DEBUG FUNCTION CALLED")
        # render_debug_info(
        #     result
        # )
        render_debug_history()
        

    st.session_state.chat_history = result["chat_history"]
    # st.rerun()
