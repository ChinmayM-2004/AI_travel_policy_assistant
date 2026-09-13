# AI Travel Policy Assistant

An AI-powered travel policy assistant that helps employees determine whether business travel requests comply with company travel policies.

The application combines Retrieval-Augmented Generation (RAG), vector search, conversational memory, MCP tools, Gemini, and a Flask web interface to provide policy-grounded travel decisions.

---

## 1. Business Problem

Employees often need quick answers about company travel policies before booking flights, hotels, airport transportation, or submitting expenses.

Manually searching through multiple policy documents can be time-consuming and may lead to:

- Incorrect interpretation of company policies
- Missing important approval requirements
- Repeated questions about the same employee or trip
- Difficulty handling follow-up questions
- Inconsistent reimbursement calculations
- Hallucinated answers when policy information is unavailable

The goal of this project is to provide a centralized AI assistant that can retrieve relevant company policies, validate employee eligibility, perform policy-based calculations, and maintain conversation context.

---

## 2. Solution

The AI Travel Policy Assistant provides:

- Policy-based question answering using RAG
- Semantic search using FAISS
- Sentence Transformer embeddings
- Employee eligibility validation
- Travel trip validation
- Reimbursement calculation
- MCP-based business tools
- Short-term conversational memory
- Multi-turn follow-up handling
- Hallucination protection for unsupported questions
- Graceful error handling
- Flask REST API
- Enterprise-style web interface

The system can operate in local development mode using deterministic application logic and can also use the Gemini-based agent workflow.

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
                  | AI Assistant   |
                  | Service Layer  |
                  +----------------+
                     /          \
                    /            \
                   v              v
          +---------------+   +-------------+
          | Conversation  |   | AI Agent    |
          | Memory        |   | Gemini      |
          +---------------+   +-------------+
                   |               |
                   |               v
                   |        +-------------+
                   |        | RAG Search  |
                   |        +-------------+
                   |               |
                   |               v
                   |        +-------------+
                   |        | FAISS       |
                   |        | Vector Store|
                   |        +-------------+
                   |
                   v
             +-------------+
             | MCP Client  |
             +-------------+
                    |
                    v
             +-------------+
             | MCP Server  |
             +-------------+
               /     |      \
              v      v       v
       Eligibility  Trip   Reimbursement
          Tool    Validation   Tool

4. Technology Stack
Programming Language
Python 3.12
AI / LLM
Google Gemini
Gemini gemini-3.6-flash
RAG
Sentence Transformers
all-MiniLM-L6-v2
FAISS
NumPy
Agent / Tools
MCP
Custom MCP server
MCP client
Gemini function/tool calling
Backend
Flask
REST API
Frontend
HTML
CSS
JavaScript
Data
JSON
TXT policy documents

5. Project Structure
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
│   │   └── metadata.json
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
│   └── prompts.py
│
├── mcp/
│   └── server.py
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
6. RAG Workflow

The RAG pipeline follows these steps:

Step 1 — Policy ingestion

The company policy TXT files are loaded from:

company_policy/
Step 2 — Metadata creation

Metadata is generated for each policy document, including information such as:

Policy source
Policy type
Country
Document information
Step 3 — Document chunking

Policy documents are divided into smaller chunks so that relevant sections can be retrieved efficiently.

The final policy dataset contains 58 chunks.

Step 4 — Embedding generation

Each policy chunk is converted into a vector using:

all-MiniLM-L6-v2

The generated embeddings have 384 dimensions.

Step 5 — FAISS indexing

The embeddings are stored in a FAISS vector index.

vector_store/policy_index.faiss
Step 6 — Query embedding

When the user asks a policy question, the question is converted into an embedding using the same model.

Step 7 — Similarity search

FAISS retrieves the most semantically similar policy chunks.

Step 8 — Relevance filtering

Only sufficiently relevant results are considered for the response.

This reduces the chance of unrelated policy documents being mixed into the answer.

Step 9 — Response generation

The retrieved policy content is used to generate the final answer.

7. Agent Workflow

The assistant supports an agentic workflow where the system can determine which capability is required.

Available capabilities include:

Policy search
Employee eligibility
Trip validation
Reimbursement calculation
Conversation memory

The Gemini agent can use tools based on the user's request.

For example:

User:
Can I take an airport trip?

        |
        v

Employee context
        |
        v

Eligibility tool
        |
        v

Policy search / trip validation
        |
        v

Final response
8. MCP Integration

The project uses the Model Context Protocol (MCP) to expose business functions as tools.

The MCP server provides three tools:

Employee Eligibility
check_employee_eligibility

Checks whether an employee is eligible for business travel.

Trip Validation
validate_trip

Validates a trip against the configured travel rules.

Reimbursement Calculation
calculate_reimbursement

Calculates the reimbursable amount and amount requiring review.

The MCP client communicates with these tools and returns structured results to the AI service.

9. Conversation Memory

The application maintains short-term conversation memory using the ConversationMemory class.

The memory stores:

User message
Assistant response
User follow-up
Assistant response

This allows follow-up questions such as:

User:
Can I take an airport trip?

Assistant:
The trip is allowed.

User:
What if it costs ₹2,500?

Assistant:
The amount exceeds the configured ₹2,000 standard limit and requires approval.

The second question can use information from the previous conversation.

10. Flask Application

The Flask application exposes the following API endpoints.

Home
GET /

Loads the web interface.

Ask
POST /ask

Example request:

{
    "employee_id": "EMP001",
    "question": "Can I take an airport trip for ₹1,500?"
}
Clear Conversation
POST /clear

Clears the current conversation memory.

Conversation History
GET /history

Returns the current conversation history.

Health Check
GET /health

Example response:

{
    "status": "healthy",
    "service": "AI Travel Policy Assistant"
}
11. Example Use Cases
India employee eligibility
Employee ID: EMP001

Question:
Am I eligible for business travel?

Expected result:

Eligible
Contractor eligibility
Employee ID: EMP002

Question:
Am I eligible for business travel?

Expected result:

Not Eligible
Airport trip within limit
Employee ID: EMP001

Question:
Can I take an airport trip for ₹1,500?

Expected result:

Approved
Airport trip exceeding limit
Employee ID: EMP001

Question:
Can I take an airport trip for ₹2,500?

Expected result:

Needs Approval
Follow-up question
User:
Can I take an airport trip?

Assistant:
The trip is allowed.

User:
What if it costs ₹2,500?

Assistant:
The trip exceeds the standard limit and requires approval.
12. Hallucination Prevention

The assistant was tested against unsupported questions.

Examples include:

What are the hotel booking rules?

and:

What is the maximum flight ticket price?

When the available policy documents do not contain the requested information, the system responds:

I could not find information about this in the available policy documents.

The system does not invent policy values.

Questions that are actually supported by the policy, such as rental car reimbursement under the applicable US policy, are answered using the retrieved policy content.

13. Error Handling

The application was tested for multiple failure scenarios.

Empty question

Returns:

Please enter a question.
Invalid employee ID

Returns a structured employee-not-found response.

Negative trip amount

Example:

₹-500

Returns:

Invalid trip amount. The trip amount cannot be negative.
Missing FAISS index

The RAG layer gracefully returns:

I could not find information about this in the available policy documents.

instead of exposing a technical exception.

Missing embedding model

The retrieval layer safely returns no results instead of crashing.

Gemini quota/API failure

The agent handles quota errors with a user-friendly message rather than exposing the raw API exception.

MCP tool failure

MCP responses are checked for tool errors before formatting the final response.

14. Testing

The project includes functional, hallucination, API, and error-handling tests.

Functional Tests

The system was tested for:

India travel policy
US travel policy
Airport travel
Late-night travel
Expense requirements
Employee eligibility
Invalid employees
India airport trips
US airport trips
Reimbursement
Multi-turn conversation

A total of at least 15 functional scenarios were tested.

Hallucination Tests

Tests included:

Unsupported hotel booking information
Unsupported maximum flight price
Supported rental car policy
Error Tests

Tests included:

Empty questions
Invalid employee IDs
Negative trip amounts
Missing policy index
API/quota failure
MCP tool input failure
Embedding/retrieval failure
API Tests

The Flask API was tested for:

/
/ask
/clear
/history
/health

Detailed test results are available in:

tests/test_cases.md
15. Prompt Evaluation

The initial prompt used the PTCF framework:

Persona
Task
Context
Format

It also included few-shot examples and structured output instructions.

Improvement 1 — Stronger grounding

The initial prompt instructed the model to use the policy, but the improved prompt explicitly required:

Only facts stated in the retrieved policy
No general travel knowledge
No invented limits
No invented approvals
No unsupported exceptions
Insufficient Information when the policy does not answer the question

This improved the Constraints component of the 4Cs.

Improvement 2 — Better employee context

The improved prompt explicitly included:

Employee ID
Country
Employee Type
Eligibility Status
Current Request
Conversation History
Retrieved Policy Content

This improved both Context and Customization.

Final Prompt Characteristics

The final prompt follows the 4Cs:

4C	Implementation
Context	Employee information, conversation history, retrieved policy
Clarity	Explicit role, task, rules and output format
Constraints	No unsupported facts or assumptions
Customization	Employee-specific and conversation-specific information
16. Limitations

The current project has several limitations.

Policy Coverage

The assistant can only answer questions supported by the available company policy documents.

Employee Dataset

The employee data is a small fictional dataset created for demonstration.

Policy Rules

Some validation rules are simplified for the capstone demonstration.

Memory

Conversation memory is currently short-term and maintained during the application session.

External Systems

The application does not currently connect to real HR, expense, booking, or approval systems.

Authentication

Employee authentication and authorization are not implemented.

Production Deployment

The Flask application is intended for demonstration and development rather than production deployment.

17. How to Run
Activate the virtual environment
source venv/bin/activate
Install dependencies
pip install -r requirements.txt
Start the Flask application
python app/app.py

The application runs on:

http://127.0.0.1:5000
Health check
curl http://127.0.0.1:5000/health

Expected:

{
    "status": "healthy",
    "service": "AI Travel Policy Assistant"
}
18. Key Project Outcomes

The completed system demonstrates:

Document ingestion
Metadata generation
Document chunking
Embedding generation
FAISS vector search
RAG-based policy retrieval
Agentic tool usage
MCP integration
Employee eligibility validation
Trip validation
Reimbursement calculation
Conversation memory
Multi-turn interaction
Hallucination prevention
Error handling
Flask REST API
Enterprise-style web interface
Prompt engineering and evaluation
19. Conclusion

The AI Travel Policy Assistant demonstrates how an enterprise policy assistant can combine RAG, vector search, agentic workflows, MCP tools, conversational memory, and a web interface into a single application.

The system provides policy-grounded answers while also performing structured business validations and handling unsupported or invalid requests gracefully.

The architecture can be extended in the future with real employee systems, travel booking platforms, expense management systems, authentication, persistent memory, and production-grade deployment.


Save with:

```text
Ctrl + O
Enter
Ctrl + X

Then verify the file:

wc -l README.md
head -20 README.md
