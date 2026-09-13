import json
from pathlib import Path


PROCESSED_DIR = Path("data/processed")

POLICY_METADATA = {
    "travel_policy_india.txt": {
        "policy_type": "travel",
        "country": "India"
    },
    "travel_policy_us.txt": {
        "policy_type": "travel",
        "country": "United States"
    },
    "airport_policy.txt": {
        "policy_type": "airport",
        "country": "All"
    },
    "employee_eligibility.txt": {
        "policy_type": "eligibility",
        "country": "All"
    },
    "expense_policy.txt": {
        "policy_type": "expense",
        "country": "All"
    },
    "cancellation_policy.txt": {
        "policy_type": "cancellation",
        "country": "All"
    },
    "approval_policy.txt": {
        "policy_type": "approval",
        "country": "All"
    }
}


def create_metadata():
    metadata = []

    for file_path in PROCESSED_DIR.glob("*.txt"):
        metadata.append({
            "source": file_path.name,
            "policy_type": POLICY_METADATA[file_path.name]["policy_type"],
            "country": POLICY_METADATA[file_path.name]["country"]
        })

    output_path = PROCESSED_DIR / "metadata.json"

    output_path.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8"
    )

    print(f"Metadata created: {output_path}")


if __name__ == "__main__":
    create_metadata()

