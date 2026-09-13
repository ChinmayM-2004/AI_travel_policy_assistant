from pathlib import Path

POLICY_DIR = Path("company_policy")

def clean_text(text):
    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n\n".join(cleaned_lines)

def save_cleaned_document(document_name, content):
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / document_name
    output_path.write_text(content, encoding="utf-8")

def load_documents():
    documents = []

    if not POLICY_DIR.exists():
        print("Policy directory not found.")
        return documents

    for file_path in POLICY_DIR.glob("*.txt"):

        try:
            content = file_path.read_text(encoding="utf-8")
            content = clean_text(content)
            if not content:
                print(f"Warning: Empty document - {file_path.name}")
                continue

            documents.append({
                "document_name": file_path.name,
                "content": content
            })
            save_cleaned_document(file_path.name, content)
        except OSError as e:
            print(f"Error reading {file_path.name}: {e}")

    return documents


if __name__ == "__main__":
    documents = load_documents()

    print(f"Total documents loaded: {len(documents)}")

    for document in documents:
        print(
            document["document_name"],
            "->",
            len(document["content"]),
            "characters"
        )
