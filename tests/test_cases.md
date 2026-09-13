cat > tests/test_cases.md <<'EOF'
# AI Travel Policy Assistant – Functional Test Cases

## Test Objective

Validate that the AI Travel Policy Assistant correctly handles:

- Policy retrieval
- Employee eligibility
- Trip validation
- Reimbursement calculations
- Conversational memory
- Hallucination prevention
- Error handling
- MCP tool invocation
- Flask API integration

---

# Part 1 – RAG / Policy Questions

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| RAG-01 | What is the standard travel limit in India? | Retrieve the India travel policy and provide the applicable limit. | Pending execution | ⏳ |
| RAG-02 | What is the standard travel limit in the US? | Retrieve the US travel policy and provide the applicable limit. | Pending execution | ⏳ |
| RAG-03 | Are airport trips allowed? | Explain that approved airport transportation is allowed according to policy. | Pending execution | ⏳ |
| RAG-04 | Are late-night trips allowed? | Answer only using available policy information; do not invent a late-night-specific rule. | Pending execution | ⏳ |
| RAG-05 | What information is required for an expense? | Mention required expense information such as date, amount, currency, business purpose and receipt. | Pending execution | ⏳ |

---

# Part 2 – Employee Eligibility

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| ELG-01 | Is EMP001 eligible? | EMP001 should be identified as Eligible. | Pending execution | ⏳ |
| ELG-02 | Is EMP002 eligible? | EMP002 should be identified as Not Eligible. | Pending execution | ⏳ |
| ELG-03 | Is EMP004 eligible? | EMP004 should be identified as Eligible. | Pending execution | ⏳ |
| ELG-04 | Provide an unknown employee ID. | System should return Employee Not Found without crashing. | Pending execution | ⏳ |

---

# Part 3 – Trip Validation

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TRIP-01 | Can EMP001 take a ₹1,500 airport trip? | Trip should be Approved because ₹1,500 is within the ₹2,000 India airport limit. | Verified – Approved | ✅ PASS |
| TRIP-02 | Can EMP001 take a ₹2,500 airport trip? | Trip should return Needs Approval because ₹2,500 exceeds the ₹2,000 policy limit. | Verified – Needs Approval | ✅ PASS |
| TRIP-03 | Can EMP003 take a $50 airport trip? | System should validate the trip using available policy/tool logic and avoid inventing an unsupported limit. | Pending execution | ⏳ |
| TRIP-04 | Can EMP003 take a $100 airport trip? | System should validate the trip using available policy/tool logic and avoid inventing an unsupported limit. | Pending execution | ⏳ |

---

# Part 4 – Conversational Memory

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| MEM-01 | Can I take an airport trip? | System should validate the airport trip for the employee. | Verified – Approved | ✅ PASS |
| MEM-02 | What if it costs ₹2,500? | System should understand that "it" refers to the previous airport trip and validate ₹2,500. | Verified – Needs Approval | ✅ PASS |

### Conversation Tested

```text
User:
Can I take an airport trip?

Assistant:
Trip validation → Approved
Amount → ₹1,500
Policy limit → ₹2,000

User:
What if it costs ₹2,500?

Assistant:
Follow-up trip validation → Needs Approval
Amount → ₹2,500
Policy limit → ₹2,000


RAG-01
Question: What is the standard travel limit in India?
Expected: Answer should be grounded in the India travel policy and include the relevant policy source.
Actual: Retrieved India travel policy content from travel_policy_india.txt and excluded unrelated US policy content.
Status: PASS

RAG-02
Question: What is the standard travel limit in the US?
Expected: Answer should be grounded in the US travel policy and include the relevant policy source.
Actual: Retrieved United States travel policy content from travel_policy_us.txt and excluded unrelated India policy content.
Status: PASS

RAG-03
Question: Are airport trips allowed?
Expected: Answer should use airport travel policy and should not require an Employee ID for a general policy question.
Actual: Retrieved airport policy content from airport_policy.txt without requesting an Employee ID.
Status: PASS

RAG-04
Question: Are late-night trips allowed?
Expected: If the policy does not provide information about late-night trips, the assistant should clearly state that the information is unavailable.
Actual: Returned "I could not find information about this in the available policy documents."
Status: PASS

RAG-05
Question: What information is required for an expense claim?
Expected: Answer should identify the required expense documentation and cite the relevant policy source.
Actual: Retrieved expense_policy.txt and identified date, amount, currency, business purpose, and receipt/digital proof of payment.
Status: PASS

ELIG-01
Question: Is EMP001 eligible for business travel?
Expected: EMP001 should be identified as eligible.
Actual: MCP eligibility tool returned status "Eligible" for EMP001.
Status: PASS

ELIG-02
Question: Is EMP002 eligible for business travel?
Expected: EMP002 should be identified as not eligible.
Actual: MCP eligibility tool returned status "Not Eligible" for EMP002.
Status: PASS

ELIG-03
Question: Is EMP004 eligible for business travel?
Expected: EMP004 should be identified as eligible.
Actual: MCP eligibility tool returned status "Eligible" for EMP004.
Status: PASS

ELIG-04
Question: Is EMP999 eligible for business travel?
Expected: Unknown employee ID should be handled gracefully without inventing employee details.
Actual: MCP eligibility tool returned "Employee Not Found" for EMP999 with null employee details.
Status: PASS

TRIP-01
Question: Can EMP001 take an airport trip for ₹1,500?
Expected: Trip should be approved because ₹1,500 is within the ₹2,000 India policy limit.
Actual: MCP validation returned "Approved" with a ₹2,000 policy limit.
Status: PASS

TRIP-02
Question: Can EMP001 take an airport trip for ₹2,500?
Expected: Trip should require approval because ₹2,500 exceeds the ₹2,000 India policy limit.
Actual: MCP validation returned "Needs Approval" with a ₹2,000 policy limit.
Status: PASS
