from pathlib import Path

DATA_DIR = Path("data")

def load_emails():
    emails = []
    for file in sorted(DATA_DIR.glob("*.txt")):
        content = file.read_text()
        emails.append({
            "filename": file.name,
            "content": content
        })
    return emails

if __name__ == "__main__":
    emails = load_emails()
    print(f"Loaded {len(emails)} emails\n")
    for email in emails:
        print(f"--- {email['filename']} ---")
        print(email['content'])
        print()