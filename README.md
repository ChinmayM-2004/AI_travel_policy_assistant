# AI Travel Policy Assistant

An AI-powered travel policy assistant that helps employees determine whether business travel requests comply with company travel policies.

The application combines **Retrieval-Augmented Generation (RAG), semantic vector search, conversational memory, MCP tools, Google Gemini, and Flask** to provide policy-grounded travel decisions through an enterprise-style web interface.

---

## 1. Business Problem

Employees often need quick answers about company travel policies before booking flights, hotels, airport transportation, or submitting expenses.

Manually searching through multiple policy documents can be time-consuming and may lead to:

* Incorrect interpretation of company policies
* Missing important approval requirements
* Repeated questions about the same employee or trip
* Difficulty handling follow-up questions
* Inconsistent reimbursement calculations
* Hallucinated answers when policy information is unavailable

The goal of this project is to provide a centralized AI assistant that can:

* Retrieve relevant company policies
* Validate employee eligibility
* Validate travel requests
* Calculate reimbursement amounts
* Maintain conversation context
* Handle unsupported questions safely

---

## 2. Solution

The AI Travel Policy Assistant provides:

* Policy-based question answering using RAG
* Semantic search using FAISS
* Sentence Transformer embeddings
* Employee eligibility validation
* Travel trip validation
* Reimbursement calculation
* MCP-based business tools
* Short-term conversational memory
* Multi-turn follow-up handling
* Hallucination protection for unsupported questions
* Graceful error handling
* Flask REST API
* Enterprise-style web interface

The system combines deterministic business logic with an AI agent workflow powered by Gemini.

---

## 3. Architecture

```text
                              USER
                                |
                                v
                       +----------------+
                       |   Flask Web UI |
                       +----------------+
                                |
                                v
                       +----------------+
                       |   Flask API    |
                       +----------------+
                                |
                                v
                       +----------------+
                       |   AI Assistant |
                       |     Service    |
                       +----------------+
                          /           \
                         /             \
                        v               v
              +----------------+   +-------------+
              | Conversation   |   | AI Agent    |
              | Memory         |   | Gemini      |
              +----------------+   +-------------+
                        |               |
                        |               v
                        |        +-------------+
                        |        | RAG Search  |
                        |        +-------------+
                        |               |
                        |               v
                        |        +-------------+
                        |        |    FAISS    |
                        |        | Vector Store|
                        |        +-------------+
                        |
                        v
                 +-------------+
                 |  MCP Client |
                 +-------------+
                        |
                        v
                 +-------------+
                 |  MCP Server |
                 +-------------+
                   /     |      \
                  v      v       v
          Eligibility   Trip   Reimbursement
             Tool    Validation    Tool
```

### High-Level Flow

```text
User
  ↓
Flask Web Interface
  ↓
Flask API
  ↓
AI Assistant Service
  ↓
Conversation Memory + AI Agent
  ↓
RAG Search / MCP Tools
  ↓
FAISS Vector Store / Business Logic
  ↓
Gemini
  ↓
Policy-Grounded Response
```

---

## 4. Technology Stack

### Programming Language

* Python 3.12

### AI / LLM

* Google Gemini
* Gemini `gemini-3.6-flash`
* Gemini function/tool calling

### RAG

* Sentence Transformers
* `all-MiniLM-L6-v2`
* FAISS
* NumPy

### Agent / Tools

* Model Context Protocol (MCP)
* Custom MCP server
* MCP client
* Gemini tool calling

### Backend

* Flask
* REST API

### Frontend

* HTML
* CSS
* JavaScript

### Data

* JSON
* TXT policy documents

---

## 5. Project Structure

```text
ai_travel_policy_assistant/
│
├── company_policy/
│   ├── travel_policy_india.txt
│   ├── travel_policy_us.txt
│   ├── airport_policy.txt
│   ├── employee_eligibility.txt
│   ├── expense_policy.txt
│   ├── cancellation_policy.txt
│   └── approval_policy.txt
│
├── data/
│   ├── employees/
│   │   └── employees.json
│   │
│   ├── processed/
│   │   ├── metadata.json
│   │   └── processed policy files
│   │
│   ├── chunks/
│   │   └── policy_chunks.json
│   │
│   └── embeddings/
│       ├── policy_embeddings.npy
│       └── embedding_metadata.json
│
├── vector_store/
│   ├── policy_index.faiss
│   └── policy_metadata.json
│
├── src/
│   ├── agent.py
│   ├── ai_service.py
│   ├── memory.py
│   ├── tools.py
│   ├── mcp_client.py
│   ├── search_policy.py
│   ├── rag_pipeline.py
│   ├── document_ingestion.py
│   ├── document_metadata.py
│   ├── document_chunking.py
│   ├── generate_embeddings.py
│   ├── vector_store.py
│   └── prompts.py
│
├── mcp/
│   ├── server.py
│   └── test_mcp.py
│
├── app/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
│
├── tests/
│   └── test_cases.md
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 6. RAG Workflow

The RAG pipeline follows these steps.

### Step 1 — Policy Ingestion

The company policy TXT files are loaded from:

```text
company_policy/
```

The project contains seven policy documents covering areas such as:

* Travel
* Airport transportation
* Employee eligibility
* Expenses
* Cancellation
* Approvals

### Step 2 — Metadata Creation

Metadata is generated for each policy document, including information such as:

* Policy source
* Policy type
* Country
* Document information

The metadata is stored under:

```text
data/processed/
```

### Step 3 — Document Chunking

The policy documents are divided into smaller chunks so relevant sections can be retrieved efficiently.

The final policy dataset contains:

```text
58 chunks
```

### Step 4 — Embedding Generation

Each policy chunk is converted into a vector using:

```text
all-MiniLM-L6-v2
```

The generated embeddings contain:

```text
384 dimensions
```

### Step 5 — FAISS Indexing

The embeddings are stored in a FAISS vector index:

```text
vector_store/policy_index.faiss
```

Metadata for the vector store is stored in:

```text
vector_store/policy_metadata.json
```

### Step 6 — Query Embedding

When a user asks a policy question, the question is converted into an embedding using the same Sentence Transformer model.

### Step 7 — Similarity Search

FAISS retrieves the most semantically similar policy chunks.

### Step 8 — Relevance Filtering

Only sufficiently relevant results are considered for the response.

This reduces the chance of unrelated policy documents being mixed into the answer.

### Step 9 — Response Generation

The retrieved policy content is passed to the response-generation workflow so that the final answer is grounded in the available company policy.

---

# 7. Agent Workflow

The assistant supports an agentic workflow where the system can determine which capability is required.

Available capabilities include:

* Policy search
* Employee eligibility
* Trip validation
* Reimbursement calculation
* Conversation memory

The Gemini agent can use tools based on the user's request.

### Example

```text
User
  |
  | "Can I take an airport trip?"
  v
Employee Context
  |
  v
Eligibility Tool
  |
  v
Policy Search / Trip Validation
  |
  v
Final Response
```

For questions involving specific employees or trip amounts, the assistant can combine employee information, policy retrieval, business tools, and conversation history.

---

# 8. MCP Integration

The project uses the **Model Context Protocol (MCP)** to expose business functions as tools.

The MCP server provides three tools.

### 1. Employee Eligibility

```text
check_employee_eligibility
```

Checks whether an employee is eligible for business travel.

### 2. Trip Validation

```text
validate_trip
```

Validates a trip against the configured travel rules.

### 3. Reimbursement Calculation

```text
calculate_reimbursement
```

Calculates:

* Reimbursable amount
* Amount requiring review

The MCP client communicates with these tools and returns structured results to the AI service.

---

# 9. Conversation Memory

The application maintains short-term conversation memory using the `ConversationMemory` class.

The memory stores:

* User messages
* Assistant responses
* Follow-up questions
* Follow-up responses

This allows multi-turn conversations.

### Example

```text
User:
Can I take an airport trip?

Assistant:
The trip is allowed.

User:
What if it costs ₹2,500?

Assistant:
The amount exceeds the configured ₹2,000 standard limit
and requires approval.
```

The second question can use information from the previous conversation.

---

# 10. Flask Application

The Flask application exposes the following API endpoints.

### Home

```text
GET /
```

Loads the web interface.

### Ask

```text
POST /ask
```

Example request:

```json
{
    "employee_id": "EMP001",
    "question": "Can I take an airport trip for ₹1,500?"
}
```

### Clear Conversation

```text
POST /clear
```

Clears the current conversation memory.

### Conversation History

```text
GET /history
```

Returns the current conversation history.

### Health Check

```text
GET /health
```

Example response:

```json
{
    "status": "healthy",
    "service": "AI Travel Policy Assistant"
}
```

---

# 11. Example Use Cases

## India Employee Eligibility

**Employee ID:**

```text
EMP001
```

**Question:**

```text
Am I eligible for business travel?
```

**Expected result:**

```text
Eligible
```

---

## Contractor Eligibility

**Employee ID:**

```text
EMP002
```

**Question:**

```text
Am I eligible for business travel?
```

**Expected result:**

```text
Not Eligible
```

---

## Airport Trip Within Limit

**Employee ID:**

```text
EMP001
```

**Question:**

```text
Can I take an airport trip for ₹1,500?
```

**Expected result:**

```text
Approved
```

---

## Airport Trip Exceeding Limit

**Employee ID:**

```text
EMP001
```

**Question:**

```text
Can I take an airport trip for ₹2,500?
```

**Expected result:**

```text
Needs Approval
```

---

## Follow-Up Question

```text
User:
Can I take an airport trip?

Assistant:
The trip is allowed.

User:
What if it costs ₹2,500?

Assistant:
The trip exceeds the standard limit and requires approval.
```

---

# 12. Hallucination Prevention

The assistant was tested against unsupported questions.

Examples include:

```text
What are the hotel booking rules?
```

and:

```text
What is the maximum flight ticket price?
```

When the available policy documents do not contain the requested information, the system responds:

```text
I could not find information about this in the available policy documents.
```

The system is designed not to invent:

* Policy values
* Approval requirements
* Reimbursement limits
* Exceptions
* Travel rules

Questions that are actually supported by the policy are answered using retrieved policy content.

For example, rental car reimbursement under the applicable US policy is treated as a supported policy question rather than incorrectly rejecting it as unsupported.

---

# 13. Error Handling

The application was tested against multiple failure scenarios.

### Empty Question

Returns:

```text
Please enter a question.
```

### Invalid Employee ID

Returns a structured employee-not-found response.

### Negative Trip Amount

Example:

```text
₹-500
```

Returns:

```text
Invalid trip amount. The trip amount cannot be negative.
```

### Missing FAISS Index

The RAG layer gracefully returns:

```text
I could not find information about this in the available policy documents.
```

instead of exposing a technical exception.

### Missing Embedding Model

The retrieval layer safely returns no results instead of crashing.

### Gemini Quota / API Failure

The agent handles quota errors with a user-friendly message instead of exposing the raw API exception.

### MCP Tool Failure

MCP responses are checked for tool errors before formatting the final response.

---

# 14. Testing

The project includes functional, hallucination, API, and error-handling tests.

## Functional Tests

The system was tested for:

* India travel policy
* US travel policy
* Airport travel
* Late-night travel
* Expense requirements
* Employee eligibility
* Invalid employees
* India airport trips
* US airport trips
* Reimbursement
* Multi-turn conversation

A total of at least **15 functional scenarios** were tested.

## Hallucination Tests

Tests included:

* Unsupported hotel booking information
* Unsupported maximum flight price
* Supported rental car policy

## Error Tests

Tests included:

* Empty questions
* Invalid employee IDs
* Negative trip amounts
* Missing policy index
* API/quota failure
* MCP tool input failure
* Embedding/retrieval failure

## API Tests

The Flask API was tested for:

```text
GET  /
POST /ask
POST /clear
GET  /history
GET  /health
```

Detailed test results are available in:

```text
tests/test_cases.md
```

---

# 15. Prompt Evaluation

The initial prompt used the **PTCF framework**:

* Persona
* Task
* Context
* Format

It also included few-shot examples and structured output instructions.

## Improvement 1 — Stronger Grounding

The improved prompt explicitly required:

* Only facts stated in the retrieved policy
* No general travel knowledge
* No invented limits
* No invented approvals
* No unsupported exceptions
* `Insufficient Information` when the policy does not answer the question

This strengthened the grounding and constraint handling of the assistant.

## Improvement 2 — Better Employee Context

The improved prompt explicitly includes:

* Employee ID
* Country
* Employee Type
* Eligibility Status
* Current Request
* Conversation History
* Retrieved Policy Content

This improves both context and employee-specific customization.

## Final Prompt Characteristics

| 4C            | Implementation                                               |
| ------------- | ------------------------------------------------------------ |
| Context       | Employee information, conversation history, retrieved policy |
| Clarity       | Explicit role, task, rules, and output format                |
| Constraints   | No unsupported facts or assumptions                          |
| Customization | Employee-specific and conversation-specific information      |

---

# 16. Limitations

The current project has several limitations.

### Policy Coverage

The assistant can only answer questions supported by the available company policy documents.

### Employee Dataset

The employee data is a small fictional dataset created for demonstration.

### Policy Rules

Some validation rules are simplified for the capstone demonstration.

### Memory

Conversation memory is currently short-term and maintained during the application session.

### External Systems

The application does not currently connect to real:

* HR systems
* Expense management systems
* Travel booking systems
* Approval systems

### Authentication

Employee authentication and authorization are not implemented.

### Production Deployment

The Flask application is intended for demonstration and development rather than production deployment.

---

# 17. How to Run

## Step 1 — Clone the Repository

```bash
git clone https://github.com/ChinmayM-2004/AI_travel_policy_assistant.git
cd AI_travel_policy_assistant
```

## Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4 — Configure the Gemini API Key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

> Do not commit the `.env` file to GitHub. It contains a private API credential.

## Step 5 — Start the Flask Application

```bash
python app/app.py
```

The application runs on:

```text
http://127.0.0.1:5000
```

## Step 6 — Health Check

Open:

```text
http://127.0.0.1:5000/health
```

Or run:

```bash
curl http://127.0.0.1:5000/health
```

Expected response:

```json
{
    "status": "healthy",
    "service": "AI Travel Policy Assistant"
}
```

---

# 18. Key Project Outcomes

The completed system demonstrates:

* Document ingestion
* Metadata generation
* Document chunking
* Embedding generation
* FAISS vector search
* RAG-based policy retrieval
* Agentic tool usage
* MCP integration
* Employee eligibility validation
* Trip validation
* Reimbursement calculation
* Conversation memory
* Multi-turn interaction
* Hallucination prevention
* Error handling
* Flask REST API
* Enterprise-style web interface
* Prompt engineering
* Prompt evaluation
* End-to-end testing

---

# 19. Future Improvements

The system can be extended with:

* Persistent conversation memory
* Real employee/HR system integration
* Travel booking integration
* Expense management integration
* Approval workflow integration
* Employee authentication and authorization
* Role-based access control
* Production-grade deployment
* Monitoring and logging
* More comprehensive policy coverage
* Automated policy document updates

---

# 20. Conclusion

The **AI Travel Policy Assistant** demonstrates how an enterprise policy assistant can combine:

* RAG
* Semantic vector search
* Agentic workflows
* MCP tools
* Conversational memory
* Gemini
* Flask
* A web interface

into a single application.

The system provides policy-grounded answers while also performing structured business validations and handling unsupported or invalid requests gracefully.

The architecture provides a foundation that can be extended with real enterprise systems, persistent memory, authentication, travel booking, expense management, approval workflows, and production-grade deployment.
