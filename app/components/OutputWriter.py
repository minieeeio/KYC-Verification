import csv
import os
from datetime import datetime

from Constants import CSV_FIELDNAMES,OUTPUT_DIR


def write_output_row(drive_file_id: str, file_name: str, status: str, validated: dict) -> None:
    """Write or update one row in output/<status>/results.csv.

    If a row for this drive_file_id already exists (e.g. from an
    earlier failed attempt that's now being retried), it's replaced
    rather than duplicated, since a CSV file has no native "update"
    operation the way a database table does.
    """
    status_dir = os.path.join(OUTPUT_DIR, status)
    os.makedirs(status_dir, exist_ok=True)
    csv_path = os.path.join(status_dir, "results.csv")

    new_row = {
        "drive_file_id": drive_file_id,
        "file_name": file_name,
        "status": status,
        "doc_type": validated.get("doc_type"),
        "full_name": validated.get("full_name"),
        "date_of_birth": validated.get("date_of_birth"),
        "id_number": validated.get("id_number"),
        "nationality": validated.get("nationality"),
        "expiry_date": validated.get("expiry_date"),
        "is_expired": validated.get("is_expired", False),
        "validation_errors": "; ".join(validated.get("validation_errors", [])),
        "processed_at": datetime.now().isoformat(),
    }

    # Read whatever rows already exist, if the file is there.
    existing_rows = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)

    updated = False
    for i, row in enumerate(existing_rows):
        if row["drive_file_id"] == drive_file_id:
            existing_rows[i] = new_row
            updated = True
            break

    if not updated:
        existing_rows.append(new_row)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(existing_rows)


def cleanup_temp_file(local_path: str) -> None:
    """Delete the downloaded temp file from input/."""
    if local_path and os.path.exists(local_path):
        os.remove(local_path)