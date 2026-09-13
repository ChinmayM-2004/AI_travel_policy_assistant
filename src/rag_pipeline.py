import os

from dotenv import load_dotenv
from google import genai

from src.search_policy import search_policy


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please check your .env file."
    )

client = genai.Client(api_key=API_KEY)


def build_rag_prompt(question, search_results):
    context_parts = []

    for i, result in enumerate(search_results, start=1):

        source = result["metadata"]["source"]
        text = result["text"]

        context_parts.append(
            f"Policy Source {i}: {source}\n"
            f"Policy Content:\n{text}"
        )

    policy_context = "\n\n".join(context_parts)

    prompt = f"""
You are an AI company travel policy assistant.

Answer the employee's question using ONLY the policy
information provided below.

IMPORTANT RULES:
1. Do not use outside knowledge.
2. Do not invent or assume company policy.
3. If the answer is not supported by the provided policy,
   say exactly:
   "I could not find information about this in the available policy documents."
4. Give a concise and clear answer.
5. Always mention the policy source used.
6. If multiple sources support the answer, mention all relevant sources.

Employee Question:
{question}

Retrieved Policy Context:
{policy_context}

Return the answer in this format:

Answer:
[Your answer]

Source:
[Policy filename(s)]
"""

    return prompt


def generate_answer(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Error generating answer: {e}"


def display_retrieved_sources(search_results):
    print("\n===== RETRIEVED POLICY SOURCES =====")

    for i, result in enumerate(search_results, start=1):

        source = result["metadata"]["source"]
        policy_type = result["metadata"]["policy_type"]
        country = result["metadata"]["country"]
        score = result["score"]

        print(f"\nSource {i}")
        print(f"Policy: {source}")
        print(f"Policy Type: {policy_type}")
        print(f"Country: {country}")
        print(f"Cosine Similarity: {score:.4f}")

        print("Retrieved Content:")
        print(result["text"])


def rag_pipeline(question, top_k=3):

    print("\nSearching company policies...")

    search_results = search_policy(
        question,
        top_k=top_k
    )

    if not search_results:

        return {
            "answer": (
                "I could not find information about this "
                "in the available policy documents."
            ),
            "sources": []
        }

    print(f"Retrieved {len(search_results)} policy chunks.")

    # Show why these documents were retrieved.
    display_retrieved_sources(search_results)

    # Build prompt using retrieved policy content.
    prompt = build_rag_prompt(
        question,
        search_results
    )

    # Generate grounded answer.
    answer = generate_answer(prompt)

    sources = []

    for result in search_results:

        source = result["metadata"]["source"]

        if source not in sources:
            sources.append(source)

    return {
        "answer": answer,
        "sources": sources
    }


def main():

    print("===== AI TRAVEL POLICY ASSISTANT =====")

    question = input(
        "\nEnter your travel policy question: "
    ).strip()

    if not question:
        print("Please enter a question.")
        return

    result = rag_pipeline(
        question,
        top_k=3
    )

    print("\n===== RAG ANSWER =====")
    print(result["answer"])

    print("\n===== SOURCES USED FOR RETRIEVAL =====")

    for source in result["sources"]:
        print(f"- {source}")


if __name__ == "__main__":
    main()