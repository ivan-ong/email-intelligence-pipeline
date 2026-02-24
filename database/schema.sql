CREATE TABLE IF NOT EXISTS `email_pipeline.extracted_emails` (
  email_id       STRING    NOT NULL,
  filename       STRING    NOT NULL,
  sender_name    STRING,
  sender_email   STRING,
  intent         STRING    NOT NULL,
  key_entities   ARRAY<STRING>,
  summary        STRING,
  processed_at   TIMESTAMP NOT NULL
);
