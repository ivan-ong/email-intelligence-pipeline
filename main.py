import logging
from pathlib import Path
from extraction.extractor import extract_from_email
from database.bigquery_client import insert_email, email_already_processed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")


def load_emails():
    emails = []
    for file in sorted(DATA_DIR.glob("*.txt")):
        content = file.read_text()
        emails.append({"filename": file.name, "content": content})
    return emails


if __name__ == "__main__":
    emails = load_emails()
    logger.info("Processing %d emails...", len(emails))

    for email in emails:
        filename = email["filename"]
        content = email["content"]

        if email_already_processed(content):
            logger.info("Skipping %s — already in database", filename)
            continue

        logger.info("Processing %s...", filename)
        try:
            extraction = extract_from_email(content)
            insert_email(filename, content, extraction)
        except Exception as e:
            logger.error("ERROR processing %s: %s", filename, e)

    logger.info("Done.")
