from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
from transformers import pipeline

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=-1
)

def generate_response(query, retrieved_chunks):

    context = "\n\n".join(retrieved_chunks)

    prompt = f"""You are a helpful assistant.

    Answer ONLY using the provided context.

    If the answer is not found in the context,
    say:
    "I could not find relevant information."

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    output = pipe(
        prompt,
        max_new_tokens=120,
        temperature=0.3,
        do_sample=True
    )

    generated_text = output[0]["generated_text"]

    answer = generated_text.split("Answer:")[-1].strip()

    return answer