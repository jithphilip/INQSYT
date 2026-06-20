# Discovered Intent Taxonomy Report (Unsupervised Clustering)

We performed unsupervised semantic clustering (K-Means, $K=10$) on the unique queries from the Bitext Customer Support Dataset using **BAAI/bge-base-en-v1.5** embeddings. 

This analysis groups queries by their underlying semantic goals, providing an empirical basis for establishing a customer support **Intent Taxonomy**.

---

## 📊 1. Intent Distribution (Cluster Size Analysis)
Here is the distribution of the discovered intents, ordered from highest to lowest volume in the dataset:

| Proposed Intent Label | Cluster ID | Size (Unique Queries) | Percentage | Core Focus Area |
| :--- | :---: | :---: | :---: | :--- |
| **`Account Management & Profile Changes`** | 5 | 4,512 | 18.32% | Switching account types, updating profile configurations, and PIN modifications. |
| **`Refunds & Credit Processing`** | 1 | 4,055 | 16.46% | Inquiries regarding checking refund status, timelines, refund eligibility, and credits. |
| **`Payment Issues & Method Management`** | 4 | 2,944 | 11.95% | Handling declined transactions, reporting payment issues, and modifying payment methods. |
| **`Delivery Status & Arrival Inquiries`** | 8 | 2,550 | 10.35% | Checking expected delivery dates and finding out when shipments are scheduled to arrive. |
| **`Order Cancellations & Corrections`** | 6 | 2,149 | 8.72% | Cancelling active orders, correcting purchases, and locating current order ETAs. |
| **`Customer Feedback & Complaints`** | 9 | 2,052 | 8.33% | Submitting customer reviews, lodging formal complaints, and leaving product feedback. |
| **`Delivery Address Modifications`** | 2 | 1,999 | 8.11% | Modifying active delivery addresses, setting secondary addresses, and updating shipping destinations. |
| **`Invoices & Billing Documents`** | 7 | 1,838 | 7.46% | Requests for invoices, bill lookups, payment summaries, and downloading billing records. |
| **`Agent Handoff & Customer Support`** | 3 | 1,538 | 6.24% | Requests to speak with a live support agent or talk to customer service representatives. |
| **`Newsletter & Subscription Management`** | 0 | 998 | 4.05% | Subscribing or unsubscribing from corporate newsletters and mailing lists. |
| **Total Deduplicated Queries** | | **24,635** | **100.00%** | |

---

## 🔍 2. Discovered Intent Profiles
Below is a detailed breakdown of each cluster, showing the most representative user questions (closest to the cluster centroid) and the dominant keywords:

### 1. `Account Management & Profile Changes` (Cluster 5)
* **Volume**: 4,512 unique queries (18.32%)
* **Description**: Inquiries regarding switching account types or modifying profile and security information.
* **Dominant Keywords**: `account`, `user`, `profile`, `change`, `switching`, `pin`, `security`
* **Representative Queries (Centroid Matches)**:
  - *"I need assistance changing to the [Account Type] account"*
  - *"I need assistance to change to the [Account Type] account"*
  - *"I need assistance switching to the [Account Type] account"*
  - *"I want help trying to switch to the [Account Type] account"*

---

### 2. `Refunds & Credit Processing` (Cluster 1)
* **Volume**: 4,055 unique queries (16.46%)
* **Description**: Inquiries regarding checking refund status, timelines, refund rules, and receiving credits.
* **Dominant Keywords**: `refund`, `moneyback`, `reimbursement`, `check`, `eligibility`, `timeline`
* **Representative Queries (Centroid Matches)**:
  - *"I want help seeing in which cases can I ask to be refunded"*
  - *"I'm trying to check in which cases can I ask for a refund"*
  - *"Need help to see in which cases can I ask for my money back"*
  - *"I need assistance to verify if I am eligible for a refund"*

---

### 3. `Payment Issues & Method Management` (Cluster 4)
* **Volume**: 2,944 unique queries (11.95%)
* **Description**: Reporting failed payments, declined cards, and managing payment methods.
* **Dominant Keywords**: `payment`, `declined`, `failed`, `notify`, `assistance`, `methods`, `cards`
* **Representative Queries (Centroid Matches)**:
  - *"I want help to notify of issues with payment"*
  - *"I want assistance to inform of issues with payment"*
  - *"I want assistance notifying of issues with payment"*
  - *"I need assistance to notify of troubles with payment"*

---

### 4. `Delivery Status & Arrival Inquiries` (Cluster 8)
* **Volume**: 2,550 unique queries (10.35%)
* **Description**: Inquiries on checking package arrival times and delivery updates.
* **Dominant Keywords**: `arrive`, `expect`, `delivery`, `when`, `check`, `assistance`
* **Representative Queries (Centroid Matches)**:
  - *"I want assistance to see when will my item arrive"*
  - *"I want assistance seeing when will my item arrive"*
  - *"I want assistance checking when will my item arrive"*
  - *"I want help to see when will my item arrive"*

---

### 5. `Order Cancellations & Corrections` (Cluster 6)
* **Volume**: 2,149 unique queries (8.72%)
* **Description**: Requests to cancel orders, modify active orders, or adjust item counts.
* **Dominant Keywords**: `cancel`, `cancellation`, `correct`, `order`, `assistance`, `remove`
* **Representative Queries (Centroid Matches)**:
  - *"I need assistance to cancel order [Order Number]"*
  - *"I want assistance to cancel order [Order Number]"*
  - *"I need to correct purchase [Order Number]"*
  - *"How do I edit my active order [Order Number]?"*

---

### 6. `Customer Feedback & Complaints` (Cluster 9)
* **Volume**: 2,052 unique queries (8.33%)
* **Description**: Submitting complaints against service, lodging reviews, or leaving feedback.
* **Dominant Keywords**: `feedback`, `complaint`, `claim`, `leave`, `customer`, `lodge`, `business`
* **Representative Queries (Centroid Matches)**:
  - *"Want help to make a consumer complaint against your company"*
  - *"Help me lodge a complaint against your business"*
  - *"Help me make a complaint against your business"*
  - *"Need to leave my feedback about a product can I get some help"*

---

### 7. `Delivery Address Modifications` (Cluster 2)
* **Volume**: 1,999 unique queries (8.11%)
* **Description**: Editing shipping and delivery destination addresses.
* **Dominant Keywords**: `address`, `shipping`, `delivery`, `modify`, `edit`, `change`, `secondary`
* **Representative Queries (Centroid Matches)**:
  - *"I want help trying to modify my delivery address"*
  - *"I need assistance trying to modify my delivery address"*
  - *"I need help modifying the delivery address"*
  - *"I want help trying to edit my delivery address"*

---

### 8. `Invoices & Billing Documents` (Cluster 7)
* **Volume**: 1,838 unique queries (7.46%)
* **Description**: Requests to locate, download, or view billing statements and invoices.
* **Dominant Keywords**: `bill`, `invoice`, `download`, `find`, `billing`, `receipt`
* **Representative Queries (Centroid Matches)**:
  - *"I want assistance seeing the bill from [Person Name]"*
  - *"I need help looking for my bill from [Person Name]"*
  - *"I need assistance to find my bill from [Person Name]"*
  - *"Need to locate the bill from [Person Name] help me"*

---

### 9. `Agent Handoff & Customer Support` (Cluster 3)
* **Volume**: 1,538 unique queries (6.24%)
* **Description**: Requests to contact a human agent, speak to support, or open a live chat.
* **Dominant Keywords**: `customer`, `speak`, `talk`, `agent`, `assistance`, `support`, `contact`
* **Representative Queries (Centroid Matches)**:
  - *"I want assistance to speak to someone"*
  - *"I want assistance to speak to somebody"*
  - *"Want assistance to speak with someone"*
  - *"I want help to talk with customer assistance"*

---

### 10. `Newsletter & Subscription Management` (Cluster 0)
* **Volume**: 998 unique queries (4.05%)
* **Description**: Subscribing or unsubscribing from mailing lists and newsletters.
* **Dominant Keywords**: `newsletter`, `subscription`, `unsubscribe`, `cancel`, `receive`
* **Representative Queries (Centroid Matches)**:
  - *"I want help unsubscribing to the corporate newsletter"*
  - *"I want help unsubscribing to the company newsletter"*
  - *"I need help unsubscribing to the company newsletter"*
  - *"I want help unsubscribing from the company newsletter"*

---

## 💡 Recommendations for Defining Intent Taxonomy
Based on the empirical distribution and query shapes discovered:
1. **Consolidate Low-Volume Intents**: Intents like `Invoices & Billing Documents` (7.46%) and `Payment Issues` (11.95%) are semantically distinct but have lower volumes. They could be combined into a single `billing_and_payments` intent.
2. **Isolate Order Modification vs. Cancellations**: Cancellations (`Order Cancellations & Corrections`) have a very high volume and distinct language (keywords like `cancel`), whereas address changes (`Delivery Address Modifications`) are action-oriented. Keeping these as separate intents will prevent routing errors.
3. **Align with WISR Rule**: The discovered clusters correspond closely to the transactional **WISR** (Where's my order, Issues, Shipping, Returns) taxonomy, showing that actual human support requests naturally group into these buckets.
