import sys
from pathlib import Path

from flask import Flask, jsonify, request, render_template


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# AI SERVICE
# ============================================================

from src.ai_service import TravelAIService


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# Create one AI service instance for the application
ai_service = TravelAIService()


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():
    """
    Render the Travel Policy Assistant dashboard.
    """

    return render_template("index.html")


# ============================================================
# ASK
# ============================================================

@app.route("/ask", methods=["POST"])
def ask():
    """
    Receive a question from the browser and
    send it to the AI service.
    """

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "Request body is required."
            }), 400


        question = data.get(
            "question",
            ""
        ).strip()

        employee_id = data.get(
            "employee_id",
            ""
        ).strip()


        if not question:

            return jsonify({
                "error": "Question is required."
            }), 400


        result = ai_service.ask(
            question=question,
            employee_id=employee_id
        )


        return jsonify(result)


    except Exception as e:

        return jsonify({
            "error": (
                "Unable to process request: "
                f"{str(e)}"
            )
        }), 500


# ============================================================
# CLEAR CONVERSATION
# ============================================================

@app.route("/clear", methods=["POST"])
def clear():
    """
    Clear the current conversation memory.
    """

    try:

        result = (
            ai_service.clear_conversation()
        )

        return jsonify(result)


    except Exception as e:

        return jsonify({
            "error": (
                "Unable to clear conversation: "
                f"{str(e)}"
            )
        }), 500


# ============================================================
# HISTORY
# ============================================================

@app.route("/history", methods=["GET"])
def history():
    """
    Return the current conversation history.
    """

    try:

        return jsonify({
            "history": ai_service.get_history()
        })


    except Exception as e:

        return jsonify({
            "error": (
                "Unable to retrieve history: "
                f"{str(e)}"
            )
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """

    return jsonify({
        "status": "healthy",
        "service": "AI Travel Policy Assistant"
    })


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )