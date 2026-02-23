from pathlib import Path
from extraction.extractor import extract_from_email
from database.bigquery_client import insert_email, email_already_processed

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
        filename = email["filename"]
        content = email["content"]

        if email_already_processed(content):
            print(f"Skipping {filename} — already in database")
            continue

        print(f"Processing {filename}...")
        try:
            extraction = extract_from_email(content)
            insert_email(filename, content, extraction)
        except Exception as e:
            print(f"ERROR processing {filename}: {e}")

    print("\nDone.")