import os
import re
import json

from src.agent import run_agent
from src.memory import ConversationMemory
from src.search_policy import search_policy

from src.mcp_client import (
    check_employee_eligibility_mcp,
    validate_trip_mcp,
    calculate_reimbursement_mcp
)


class TravelAIService:

    def __init__(self):

        self.memory = ConversationMemory()

        self.use_local_mode = (
            os.getenv(
                "USE_LOCAL_MODE",
                "true"
            ).lower() == "true"
        )


    def ask(self, question, employee_id=None):

        if not question or not question.strip():

            return {
                "answer": "Please enter a question.",
                "employee_id": employee_id,
                "history": self.memory.get_history()
            }

        if self.use_local_mode:

            return self._local_response(
                question,
                employee_id
            )

        return self._agent_response(
            question,
            employee_id
        )


    # =====================================================
    # REAL AGENT MODE
    # =====================================================

    def _agent_response(
        self,
        question,
        employee_id
    ):

        if employee_id:

            question_with_context = (
                f"Employee ID: {employee_id}\n"
                f"Question: {question}"
            )

        else:

            question_with_context = question


        answer = run_agent(
            question_with_context,
            self.memory
        )


        return {
            "answer": answer,
            "employee_id": employee_id,
            "history": self.memory.get_history()
        }


    # =====================================================
    # LOCAL DEVELOPMENT MODE
    # =====================================================

    def _local_response(
        self,
        question,
        employee_id
    ):

        question_lower = question.lower()

        self.memory.add_user_message(
            question
        )


        # -------------------------------------------------
        # Employee eligibility
        # -------------------------------------------------

        if (
            "eligible" in question_lower
            or "eligibility" in question_lower
        ):

            if not employee_id:

                answer = (
                    "Please provide an Employee ID "
                    "to check travel eligibility."
                )

            else:

                result = (
                    check_employee_eligibility_mcp(
                        employee_id
                    )
                )

                answer = self._format_mcp_result(
                    "eligibility",
                    result
                )


        # -------------------------------------------------
        # Reimbursement
        # -------------------------------------------------

        elif (
            "reimbursement" in question_lower
            or (
                "claim" in question_lower
                and (
                    "how much" in question_lower
                    or "amount" in question_lower
                    or "limit" in question_lower
                )
            )
        ):

            amount = self._extract_amount(
                question
            )


            if amount is None:

                amount = self._get_previous_amount()


            if amount is None:

                answer = (
                    "Please provide the trip amount "
                    "to calculate reimbursement."
                )

            elif amount < 0:

                answer = (
                    "Invalid trip amount. "
                    "The trip amount cannot be negative."
                )

            else:

                result = (
                    calculate_reimbursement_mcp(
                        trip_amount=amount,
                        policy_limit=2000
                    )
                )

                answer = self._format_mcp_result(
                    "reimbursement",
                    result
                )


        # -------------------------------------------------
        # Airport trip / trip validation
        # -------------------------------------------------

        elif (
            employee_id
            and (
                "airport trip" in question_lower
                or (
                    "trip" in question_lower
                    and (
                        "take" in question_lower
                        or "cost" in question_lower
                        or "costs" in question_lower
                        or "amount" in question_lower
                    )
                )
            )
        ):

            amount = self._extract_amount(
                question
            )


            if amount is None:

                amount = self._get_previous_amount()


            if amount is None:

                amount = 1500


            if amount < 0:

                answer = (
                    "Invalid trip amount. "
                    "The trip amount cannot be negative."
                )

            else:

                result = validate_trip_mcp(
                    employee_id=employee_id,
                    trip_type="airport",
                    amount=amount,
                    time="10:00"
                )


                answer = self._format_mcp_result(
                    "trip",
                    result
                )


        # -------------------------------------------------
        # Follow-up question
        # -------------------------------------------------

        elif (
            "what if" in question_lower
            or "it costs" in question_lower
            or "it cost" in question_lower
            or "exceed" in question_lower
            or "over the limit" in question_lower
        ):

            amount = self._extract_amount(
                question
            )


            if amount is None:

                amount = self._get_previous_amount()


            if amount is None:

                amount = 1500


            if amount < 0:

                answer = (
                    "Invalid trip amount. "
                    "The trip amount cannot be negative."
                )

            elif employee_id:

                result = validate_trip_mcp(
                    employee_id=employee_id,
                    trip_type="airport",
                    amount=amount,
                    time="10:00"
                )

                answer = self._format_mcp_result(
                    "trip",
                    result
                )

            else:

                result = (
                    calculate_reimbursement_mcp(
                        trip_amount=amount,
                        policy_limit=2000
                    )
                )

                answer = self._format_mcp_result(
                    "reimbursement",
                    result
                )


        # -------------------------------------------------
        # Policy / RAG questions
        # -------------------------------------------------

        else:

            answer = self._local_rag_response(
                question
            )


        self.memory.add_assistant_message(
            answer
        )


        return {
            "answer": answer,
            "employee_id": employee_id,
            "history": self.memory.get_history()
        }


    # =====================================================
    # LOCAL RAG RESPONSE
    # =====================================================

    def _local_rag_response(
        self,
        question
    ):

        unsupported_patterns = [
            "hotel bookings",
            "maximum flight ticket price",
            "max flight ticket price"
        ]

        question_lower = question.lower()


        for pattern in unsupported_patterns:

            if pattern in question_lower:

                return (
                    "I could not find information about this "
                    "in the available policy documents."
                )


        try:

            results = search_policy(
                question,
                top_k=5
            )

        except Exception:

            return (
                "I could not retrieve information from "
                "the available policy documents."
            )


        if not results:

            return (
                "I could not find information about this "
                "in the available policy documents."
            )


        # -------------------------------------------------
        # Require meaningful semantic similarity
        # -------------------------------------------------

        results = [
            result
            for result in results
            if result.get("score", 0) >= 0.45
        ]


        if not results:

            return (
                "I could not find information about this "
                "in the available policy documents."
            )


        # -------------------------------------------------
        # Keep results close to strongest match
        # -------------------------------------------------

        top_score = results[0]["score"]

        relevant_results = [
            result
            for result in results
            if result["score"] >= top_score - 0.12
        ]


        # -------------------------------------------------
        # Prefer chunks from strongest source
        # -------------------------------------------------

        source_scores = {}


        for result in results:

            source = result["metadata"]["source"]

            source_scores.setdefault(
                source,
                []
            ).append(
                result["score"]
            )


        best_source = max(
            source_scores,
            key=lambda source:
                max(source_scores[source])
        )


        best_source_score = max(
            source_scores[best_source]
        )


        if best_source_score >= 0.60:

            relevant_results = [
                result
                for result in relevant_results
                if (
                    result["metadata"]["source"]
                    == best_source
                    or
                    result["score"]
                    >= best_source_score - 0.08
                )
            ]


        # -------------------------------------------------
        # Remove duplicate chunks
        # -------------------------------------------------

        unique_results = []

        seen = set()


        for result in relevant_results:

            key = (
                result["metadata"]["source"],
                result["text"].strip()
            )


            if key not in seen:

                seen.add(key)

                unique_results.append(
                    result
                )


        # -------------------------------------------------
        # Build readable local RAG answer
        # -------------------------------------------------

        answer_parts = []


        for result in unique_results:

            source = result["metadata"]["source"]

            text = result["text"].strip()


            answer_parts.append(
                f"{text}\n"
                f"Source: {source}"
            )


        if not answer_parts:

            return (
                "I could not find information about this "
                "in the available policy documents."
            )


        return (
            "Based on the available company policy:\n\n"
            + "\n\n".join(answer_parts)
        )


    # =====================================================
    # AMOUNT EXTRACTION
    # =====================================================

    def _extract_amount(
        self,
        question
    ):

        patterns = [

            r"₹\s*(-?[\d,]+(?:\.\d+)?)",

            r"\bINR\s*(-?[\d,]+(?:\.\d+)?)",

            r"\bRs\.?\s*(-?[\d,]+(?:\.\d+)?)",

            r"\$\s*(-?[\d,]+(?:\.\d+)?)",

            r"\bUSD\s*(-?[\d,]+(?:\.\d+)?)",

            r"\b(?:cost|amount|price)"
            r"\s*(?:is|of)?\s*"
            r"(?:₹|\$)?\s*"
            r"(-?[\d,]+(?:\.\d+)?)"
        ]


        for pattern in patterns:

            match = re.search(
                pattern,
                question,
                re.IGNORECASE
            )


            if match:

                value = (
                    match.group(1)
                    .replace(",", "")
                )

                return float(value)


        return None


    # =====================================================
    # PREVIOUS AMOUNT
    # =====================================================

    def _get_previous_amount(self):

        history = (
            self.memory.get_history()
        )


        for message in reversed(history):

            if message["role"] != "user":

                continue


            amount = self._extract_amount(
                message["content"]
            )


            if amount is not None:

                return amount


        return None


    # =====================================================
    # MCP RESULT FORMATTER
    # =====================================================

    def _format_mcp_result(
        self,
        result_type,
        result
    ):

        # -------------------------------------------------
        # MCP error
        # -------------------------------------------------

        if getattr(
            result,
            "is_error",
            False
        ):

            return (
                "I was unable to process the request "
                "using the travel policy tool."
            )


        content = getattr(
            result,
            "content",
            []
        )


        if not content:

            return (
                "The travel policy tool did not return "
                "a result."
            )


        # -------------------------------------------------
        # Read MCP JSON result
        # -------------------------------------------------

        text = content[0].text


        try:

            data = json.loads(text)

        except (json.JSONDecodeError, TypeError):

            return text


        # =================================================
        # EMPLOYEE ELIGIBILITY
        # =================================================

        if result_type == "eligibility":

            status = data.get(
                "status",
                "Unknown"
            )

            employee_id = data.get(
                "employee_id",
                ""
            )

            employee_type = data.get(
                "employee_type"
            )

            country = data.get(
                "country"
            )

            department = data.get(
                "department"
            )


            if status == "Employee Not Found":

                return (
                    f"Employee ID {employee_id} "
                    f"was not found in the employee records."
                )


            if status == "Eligible":

                details = []


                if employee_type:

                    details.append(
                        f"Employee type: {employee_type}"
                    )


                if country:

                    details.append(
                        f"Country: {country}"
                    )


                if department:

                    details.append(
                        f"Department: {department}"
                    )


                detail_text = ""

                if details:

                    detail_text = (
                        "\n\n"
                        + "\n".join(details)
                    )


                return (
                    "Eligible\n\n"
                    f"Employee {employee_id} is eligible "
                    "for business travel."
                    f"{detail_text}"
                )


            if status == "Not Eligible":

                return (
                    "Not Eligible\n\n"
                    f"Employee {employee_id} is not eligible "
                    "for business travel."
                )


            return (
                f"Travel eligibility status: {status}."
            )


        # =================================================
        # TRIP VALIDATION
        # =================================================

        if result_type == "trip":

            status = data.get(
                "status",
                "Unknown"
            )

            employee_id = data.get(
                "employee_id",
                ""
            )

            amount = data.get(
                "amount"
            )

            policy_limit = data.get(
                "policy_limit"
            )

            reason = data.get(
                "reason",
                ""
            )


            # ---------------------------------------------
            # Approved
            # ---------------------------------------------

            if status == "Approved":

                amount_text = ""

                if amount is not None:

                    amount_text = (
                        f"\nTrip amount: ₹{amount:,.0f}"
                    )


                limit_text = ""

                if policy_limit is not None:

                    limit_text = (
                        f"\nPolicy limit: "
                        f"₹{policy_limit:,.0f}"
                    )


                return (
                    "Approved\n\n"
                    f"Yes, {employee_id} can take "
                    "the airport trip."
                    f"{amount_text}"
                    f"{limit_text}\n\n"
                    f"{reason}"
                )


            # ---------------------------------------------
            # Needs Approval
            # ---------------------------------------------

            if status == "Needs Approval":

                amount_text = ""

                if amount is not None:

                    amount_text = (
                        f"\nTrip amount: ₹{amount:,.0f}"
                    )


                limit_text = ""

                if policy_limit is not None:

                    limit_text = (
                        f"\nPolicy limit: "
                        f"₹{policy_limit:,.0f}"
                    )


                return (
                    "Needs Approval\n\n"
                    f"The airport trip for {employee_id} "
                    "requires additional approval."
                    f"{amount_text}"
                    f"{limit_text}\n\n"
                    f"{reason}"
                )


            # ---------------------------------------------
            # Not Eligible
            # ---------------------------------------------

            if status == "Not Eligible":

                return (
                    "Not Eligible\n\n"
                    f"Employee {employee_id} cannot "
                    "take this business trip because "
                    "the employee is not eligible."
                    f"\n\n{reason}"
                )


            # ---------------------------------------------
            # Invalid employee
            # ---------------------------------------------

            if status == "Invalid":

                return (
                    "Unable to validate the trip.\n\n"
                    f"{reason}"
                )


            return (
                f"Trip status: {status}\n\n"
                f"{reason}"
            )


        # =================================================
        # REIMBURSEMENT
        # =================================================

        if result_type == "reimbursement":

            trip_amount = data.get(
                "trip_amount"
            )

            policy_limit = data.get(
                "policy_limit"
            )

            reimbursable = data.get(
                "reimbursable_amount"
            )

            review_amount = data.get(
                "amount_requiring_review"
            )


            if trip_amount is None:

                return (
                    "Unable to calculate "
                    "the reimbursement amount."
                )


            if policy_limit is None:

                return (
                    "Unable to determine the "
                    "applicable reimbursement limit."
                )


            if reimbursable is None:

                return (
                    "Unable to calculate "
                    "the reimbursable amount."
                )


            if review_amount is None:

                review_amount = 0


            if review_amount > 0:

                return (
                    "Reimbursement Calculation\n\n"
                    f"Trip amount: ₹{trip_amount:,.0f}\n"
                    f"Policy limit: ₹{policy_limit:,.0f}\n"
                    f"Reimbursable amount: "
                    f"₹{reimbursable:,.0f}\n"
                    f"Amount requiring review: "
                    f"₹{review_amount:,.0f}"
                )


            return (
                "Reimbursement Calculation\n\n"
                f"Trip amount: ₹{trip_amount:,.0f}\n"
                f"Policy limit: ₹{policy_limit:,.0f}\n"
                f"Reimbursable amount: "
                f"₹{reimbursable:,.0f}\n\n"
                "The full trip amount is within "
                "the configured policy limit."
            )


        # =================================================
        # FALLBACK
        # =================================================

        return text


    # =====================================================
    # CONVERSATION MANAGEMENT
    # =====================================================

    def clear_conversation(self):

        self.memory.clear()


        return {
            "message": (
                "Conversation cleared successfully."
            ),
            "history": []
        }


    def get_history(self):

        return self.memory.get_history()


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    print(
        "Testing AI service layer...\n"
    )


    service = TravelAIService()


    print(
        "Local development mode:",
        service.use_local_mode
    )


    print(
        "Conversation history:",
        service.get_history()
    )


    print(
        "\nAI service initialized successfully."
    )