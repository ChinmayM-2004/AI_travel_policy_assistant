import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.rag_pipeline import rag_pipeline
from src.memory import ConversationMemory

from src.mcp_client import (
    check_employee_eligibility_mcp,
    validate_trip_mcp,
    calculate_reimbursement_mcp
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# POLICY SEARCH TOOL
# ============================================================

def search_company_policy(query):
    """
    Search company travel policy using RAG.
    """

    return rag_pipeline(query)


# ============================================================
# MCP TOOL WRAPPERS
# ============================================================

def check_employee_eligibility(employee_id: str):
    """
    Check employee eligibility through MCP.
    """

    return check_employee_eligibility_mcp(
        employee_id
    )


def validate_trip(
    employee_id: str,
    trip_type: str,
    amount: float,
    time: str
):
    """
    Validate a trip through MCP.
    """

    return validate_trip_mcp(
        employee_id,
        trip_type,
        amount,
        time
    )


def calculate_reimbursement(
    trip_amount: float,
    policy_limit: float
):
    """
    Calculate reimbursement through MCP.
    """

    return calculate_reimbursement_mcp(
        trip_amount,
        policy_limit
    )


# ============================================================
# GEMINI TOOL DEFINITIONS
# ============================================================

travel_tools = types.Tool(
    function_declarations=[

        types.FunctionDeclaration(
            name="search_company_policy",
            description=(
                "Search the company travel policy "
                "for policy-related questions."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query": types.Schema(
                        type="STRING",
                        description=(
                            "Question or topic to search "
                            "in the travel policy."
                        )
                    )
                },
                required=["query"]
            )
        ),

        types.FunctionDeclaration(
            name="check_employee_eligibility",
            description=(
                "Check whether an employee is eligible "
                "for business travel."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "employee_id": types.Schema(
                        type="STRING",
                        description="Employee ID."
                    )
                },
                required=["employee_id"]
            )
        ),

        types.FunctionDeclaration(
            name="validate_trip",
            description=(
                "Validate an employee trip using "
                "the configured travel policy."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "employee_id": types.Schema(
                        type="STRING"
                    ),
                    "trip_type": types.Schema(
                        type="STRING"
                    ),
                    "amount": types.Schema(
                        type="NUMBER"
                    ),
                    "time": types.Schema(
                        type="STRING"
                    )
                },
                required=[
                    "employee_id",
                    "trip_type",
                    "amount",
                    "time"
                ]
            )
        ),

        types.FunctionDeclaration(
            name="calculate_reimbursement",
            description=(
                "Calculate the reimbursable amount "
                "and amount requiring review."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "trip_amount": types.Schema(
                        type="NUMBER"
                    ),
                    "policy_limit": types.Schema(
                        type="NUMBER"
                    )
                },
                required=[
                    "trip_amount",
                    "policy_limit"
                ]
            )
        )
    ]
)


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(tool_name, tool_args):

    if tool_name == "search_company_policy":

        return search_company_policy(
            tool_args["query"]
        )

    if tool_name == "check_employee_eligibility":

        return check_employee_eligibility(
            tool_args["employee_id"]
        )

    if tool_name == "validate_trip":

        return validate_trip(
            tool_args["employee_id"],
            tool_args["trip_type"],
            tool_args["amount"],
            tool_args["time"]
        )

    if tool_name == "calculate_reimbursement":

        return calculate_reimbursement(
            tool_args["trip_amount"],
            tool_args["policy_limit"]
        )

    return {
        "error": f"Unknown tool: {tool_name}"
    }


# ============================================================
# GEMINI ERROR HANDLING
# ============================================================

def is_quota_error(error):
    """
    Detect Gemini quota/rate-limit errors.
    """

    error_text = str(error).lower()

    return (
        "429" in error_text
        or "resource_exhausted" in error_text
        or "quota" in error_text
        or "rate limit" in error_text
    )


# ============================================================
# AGENT
# ============================================================

def run_agent(question, memory):
    """
    Run the AI Travel Policy Agent.

    Uses:
    - Conversational memory
    - RAG
    - MCP tools
    - Gemini reasoning
    """

    conversation_history = (
        memory.get_formatted_history()
    )

    enhanced_question = f"""
You are the AI Travel Policy Assistant.

You help employees understand and validate
company travel policies.

Previous Conversation:
{conversation_history}

Current User Question:
{question}

Use the previous conversation to understand
follow-up questions and references such as:

- "it"
- "that"
- "the limit"
- "the trip"
- "that amount"

If the question requires company policy information,
use the search_company_policy tool.

If the question requires employee-specific information,
use the check_employee_eligibility tool.

If the question requires trip validation,
use the validate_trip tool.

If the question requires reimbursement calculation,
use the calculate_reimbursement tool.

You may use multiple tools when necessary.

Do not invent company policy.

Give a concise and clear answer.
"""

    # ========================================================
    # FIRST GEMINI REQUEST
    # ========================================================

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=enhanced_question,
            config=types.GenerateContentConfig(
                tools=[travel_tools]
            )
        )

    except Exception as e:

        if is_quota_error(e):

            return (
                "Gemini API quota has been exhausted. "
                "Please try again after the quota resets."
            )

        raise


    # ========================================================
    # TOOL-CALL LOOP
    # ========================================================

    max_rounds = 7

    for _ in range(max_rounds):

        function_calls = []

        if response.candidates:

            for candidate in response.candidates:

                if candidate.content:

                    for part in candidate.content.parts:

                        if part.function_call:

                            function_calls.append(
                                part.function_call
                            )

        # ----------------------------------------------------
        # FINAL ANSWER
        # ----------------------------------------------------

        if not function_calls:

            answer = response.text

            memory.add_user_message(
                question
            )

            memory.add_assistant_message(
                answer
            )

            return answer

        # ----------------------------------------------------
        # EXECUTE MCP/RAG TOOLS
        # ----------------------------------------------------

        tool_responses = []

        for function_call in function_calls:

            tool_name = function_call.name

            tool_args = dict(
                function_call.args
            )

            result = execute_tool(
                tool_name,
                tool_args
            )

            tool_responses.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={
                        "result": result
                    }
                )
            )

        # ----------------------------------------------------
        # CONTINUE GEMINI
        # ----------------------------------------------------

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    enhanced_question,
                    response.candidates[0].content,
                    types.Content(
                        role="user",
                        parts=tool_responses
                    )
                ],
                config=types.GenerateContentConfig(
                    tools=[travel_tools]
                )
            )

        except Exception as e:

            if is_quota_error(e):

                return (
                    "Gemini API quota has been exhausted "
                    "while completing the tool workflow. "
                    "Please try again after the quota resets."
                )

            raise


    return (
        "I could not complete the request because "
        "the tool workflow exceeded the allowed steps."
    )


# ============================================================
# INTERACTIVE TEST
# ============================================================

if __name__ == "__main__":

    memory = ConversationMemory()

    print("AI Travel Policy Assistant")
    print("Type 'exit' to stop.\n")

    while True:

        question = input("You: ")

        if question.lower() in {
            "exit",
            "quit"
        }:
            break

        try:

            answer = run_agent(
                question,
                memory
            )

            print("\nAssistant:")
            print(answer)
            print()

        except Exception as e:

            print(
                f"\nError: {e}\n"
            )