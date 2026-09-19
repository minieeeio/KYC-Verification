import sqlite3
import re

from datetime import datetime, date

class SQLdb(object):
    def __init__(self):
        print("Initialization for Database")
        self.conn=None
        self.cursor=None
        self.connect_db()
        
        
    def connect_db(self):
        self.conn=sqlite3.connect("KYC_Verification.db")
        self.cursor=self.conn.cursor()
        
    def setup_deduplication(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS  processed_documents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drive_file_id TEXT UNIQUE NOT NULL,
            file_name TEXT,
            file_hash TEXT,
            status TEXT NOT NULL,
            error_message TEXT,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )      
        """)
        self.conn.commit()
        
    def check_deduplication(self,drive_file_id):
        
        self.cursor.execute(
            "SELECT status FROM processed_documents WHERE drive_file_id=?",
            (drive_file_id,)
        )
        row=self.cursor.fetchone()
        return row[0] if row else "not_found"

    def record(self, drive_file_id, file_name, status,  error_message=None):
        self.cursor.execute("""
            INSERT INTO processed_documents
                (drive_file_id, file_name, status, error_message, processed_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(drive_file_id) DO UPDATE SET
                file_name = excluded.file_name,
                status = excluded.status,
                error_message = excluded.error_message,
                processed_at = excluded.processed_at
        """, 
        (drive_file_id, file_name, status, error_message))
        self.conn.commit()
          

    def KYC_Validation(self,parsed: dict) -> dict:
        errors = list(parsed.get("validation_errors", []))  # keep OCR-stage errors
        required_fields = ["doc_type", "full_name", "date_of_birth", "id_number"]

        # Rule 1: required fields non-empty
        # (already checked in OCR.py, but re-checked here in case this
        # function is ever called independently of that step)
        for field in required_fields:
            if not parsed.get(field):
                msg = f"{field} missing"
                if msg not in errors:
                    errors.append(msg)

        # Rule 2: date format — all dates parseable after normalisation
        parsed_dob = None
        parsed_expiry = None

        dob_raw = parsed.get("date_of_birth")
        if dob_raw:
            try:
                parsed_dob = datetime.strptime(dob_raw, "%Y-%m-%d").date()
            except ValueError:
                errors.append(f"date_of_birth not parseable: {dob_raw!r}")

        expiry_raw = parsed.get("expiry_date")
        if expiry_raw:  # optional field — only validate if present
            try:
                parsed_expiry = datetime.strptime(expiry_raw, "%Y-%m-%d").date()
            except ValueError:
                errors.append(f"expiry_date not parseable: {expiry_raw!r}")

        # Rule 3: DOB sanity — must be in the past and > 1900
        if parsed_dob is not None:
            if parsed_dob >= date.today():
                errors.append(f"date_of_birth is not in the past: {dob_raw!r}")
            elif parsed_dob.year <= 1900:
                errors.append(f"date_of_birth year is not > 1900: {dob_raw!r}")

        # Rule 4: expiry check — flag, not a validation error
        is_expired = False
        if parsed_expiry is not None:
            is_expired = parsed_expiry < date.today()

        # Rule 5: ID format — 6-12 alphanumeric characters
        id_number = parsed.get("id_number")
        if id_number:
            if not re.fullmatch(r"[A-Za-z0-9]{6,12}", id_number):
                errors.append(f"id_number format invalid: {id_number!r}")

        parsed["validation_errors"] = errors
        parsed["is_expired"] = is_expired
        return parsed
    
    def get_final_status(self,validated):
        required_fields = ["doc_type", "full_name", "date_of_birth", "id_number"]

        # Check required fields
        has_required_missing = any(
            "missing" in err or "could not be extracted" in err
            for err in validated["validation_errors"]
        )

        # Check optional fields
        has_optional_missing = (
            not validated.get("nationality")
            or not validated.get("expiry_date")
        )

        # Calculate score
        ocr_confidence = validated.get("confidence_score", 0)

        extracted_count = sum(
            1 for field in required_fields
            if validated.get(field)
        )

        field_completeness = (extracted_count / len(required_fields)) * 100

        combined_score = (
            ocr_confidence * 0.6
            + field_completeness * 0.4
        )

        # Decide status
        if combined_score >= 80 and not has_required_missing:
            final_status = "processed"
        elif combined_score >= 50 or has_optional_missing:
            final_status = "flagged"
        else:
            final_status = "failed"

        # Expired document cannot be processed
        if final_status == "processed" and validated.get("is_expired"):
            final_status = "flagged"

        return final_status
        
        
    
        
        