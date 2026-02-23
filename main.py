from pathlib import Path
from extraction.extractor import extract_from_email

DATA_DIR = Path("data")

def load_emails():
    emails = []
    for file in sorted(DATA_DIR.glob("*.txt")):
        content = file.read_text()
        emails.append({"filename": file.name, "content": content})
    return emails

if __name__ == "__main__":
    emails = load_emails()
    print(f"Processing {len(emails)} emails...\n")

    for email in emails:
        print(f"--- {email['filename']} ---")
        try:
            result = extract_from_email(email["content"])
            print(result.model_dump_json(indent=2))
        except Exception as e:
            print(f"ERROR: {e}")
        print()