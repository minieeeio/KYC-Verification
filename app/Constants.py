"""Non-secret configuration constants for the bot.

All secret credentials are fetched in QREnv vaults .
Update these values before deployment.
"""

import os 

CSV_FIELDNAMES = [
    "drive_file_id", "file_name", "status",
    "doc_type", "full_name", "date_of_birth", "id_number",
    "nationality", "expiry_date", "is_expired",
    "validation_errors", "processed_at",
]

OUTPUT_DIR = "./output"

KYC_FOLDERID=os.getenv("FOLDER_ID")
INPUT_DIR="./input"

PROCESSED_FOLDER_ID = os.getenv("PROCESSED_FOLDER_ID")
FLAGGED_FOLDER_ID = os.getenv("FLAGGED_FOLDER_ID")
FAILED_FOLDER_ID = os.getenv("FAILED_FOLDER_ID")


STATUS_FOLDER_MAP = {
    "processed": PROCESSED_FOLDER_ID,
    "flagged": FLAGGED_FOLDER_ID,
    "failed": FAILED_FOLDER_ID,
}

MODEL_NAME="gemini-3.6-flash"
OCR_PROMPT ="""
You are extracting structured KYC fields from the raw OCR text of an
identity document (passport, driving licence, national ID, or
citizenship document).

The identity document may be written entirely in English, entirely in
Nepali, or contain a mixture of Nepali and English text. Nepali text
may use the Devanagari script. You must be able to interpret Nepali
labels and values and map them to the corresponding fields in the
English JSON output below.

Extract the following fields from the text below:

doc_type (required, never null): one of "passport", "driving_licence",
"national_id", or "citizenship" — identified by keywords such as
PASSPORT, DRIVING LICENCE, NATIONAL ID, CITIZENSHIP, or their Nepali
equivalents. Return the value in lowercase with underscores, exactly
as shown above.

When the document is in Nepali, interpret the meaning of the Nepali
document title and related keywords rather than requiring the English
words to be present. For example, a Nepali citizenship document may
contain terms such as "नागरिकता प्रमाणपत्र" or other Nepali wording
identifying citizenship. Do not require an exact literal keyword
match when the same meaning is clearly expressed in Nepali.

full_name (required, never null): the person's full name. If the text
has separate "Surname" and "Given Names" lines, combine them as
"GIVEN NAMES SURNAME" (given names first, surname last). If it has a
single "Name:" line instead, use that value directly.

The name may be written in English/Latin script or Nepali/Devanagari
script. If the person's name appears in Nepali, preserve the name in
its original Nepali/Devanagari form unless an English/Latin-script
version of the same name is explicitly present in the document.
Do not transliterate, translate, or invent an English spelling when
only the Nepali name is present.

If the Nepali document uses separate fields corresponding to surname,
family name, given name, or other name components, interpret their
meaning and combine them according to the same rule above: given
names first and surname/family name last when the document clearly
identifies those components.

date_of_birth (required, never null): found near "Date of Birth",
"DOB", or "Born". The source may be in any of these formats:
"DD MMM YYYY", "YYYY-MM-DD", or "DD/MM/YYYY". Normalise the result to
"YYYY-MM-DD".

The date may also be written using Nepali labels or Nepali/Devanagari
text. Interpret Nepali labels that indicate date of birth, such as
"जन्म मिति" or equivalent wording. Do not require the English
"Date of Birth", "DOB", or "Born" labels.

The date may use either Gregorian (AD) or Nepali Bikram Sambat (BS)
calendar notation. If the document clearly identifies a date as
Bikram Sambat/BS (for example, through "वि.सं.", "बि.सं.", "B.S.",
or equivalent Nepali wording), correctly interpret the date as a
Nepali calendar date before converting it to the required
Gregorian "YYYY-MM-DD" format.

If both BS and AD/Gregorian dates are explicitly present for the same
field, use the explicitly corresponding Gregorian/AD date for the
output when available. Do not guess a BS-to-AD conversion if the
calendar system is unclear.

id_number (required, never null): a 6-12 character alphanumeric
identifier found near "No.", "Number", "Document No", or
"Licence No".

The identifier may appear near Nepali labels or wording that
corresponds to document number, citizenship number, identification
number, licence number, or similar identifying-number fields. Interpret
the meaning of the Nepali label rather than requiring the English
labels to be present.

Preserve the identifier exactly as it appears in the OCR text after
stripping unnecessary surrounding whitespace. Do not translate,
reformat, or invent characters. If OCR has clearly separated
characters belonging to the same identifier, combine them only when
the document context makes this unambiguous.

nationality (optional, may be null): found near "Nationality" or
"Country". This field is allowed to be genuinely absent from the
document.

The nationality may be written in Nepali/Devanagari. Interpret Nepali
labels corresponding to nationality or country, such as "राष्ट्रियता"
or equivalent wording. Return the extracted nationality in the
language/script in which it appears unless an explicit English/Latin
version is also provided. Do not infer nationality from the person's
name, location, citizenship document type, or other indirect clues.

expiry_date (optional, may be null): found near "Expiry",
"Valid Until", "Date of Expiry", or "Expires". Same source formats
and normalisation as date_of_birth. This field is allowed to be
genuinely absent from the document.

The expiry date may also be identified using Nepali labels or wording
corresponding to expiry, validity, or valid-until information. Do not
require the English labels to be present.

If the expiry date is explicitly written in Bikram Sambat/BS, convert
it to the required Gregorian "YYYY-MM-DD" format using the same
calendar interpretation rules described for date_of_birth. If the
calendar system is unclear, do not guess.

Rules:

Strip extra whitespace and newlines from every extracted value.
Do not guess, infer, or invent a value that is not actually present
in the text.
The document may be entirely in English, entirely in Nepali, or a
mixture of English and Nepali. Always interpret the meaning of the
available text regardless of language or script.
Nepali labels and field names should be semantically mapped to the
corresponding English JSON field names. The JSON keys themselves
must always remain exactly as specified below.
Do not require English keywords when an equivalent Nepali label or
wording clearly identifies the field.
Preserve extracted names and nationality values in their original
script when only Nepali/Devanagari is present. Do not translate or
transliterate values unless the document itself provides the
corresponding English/Latin version.
Pay attention to Nepali numerals (Devanagari digits) as well as
Western/Arabic numerals. If a date or identifier is written using
Nepali numerals, interpret the numerals correctly before producing
the required output format.
When a date is written using Nepali/Bikram Sambat calendar notation,
distinguish it from a Gregorian/AD date. Convert an explicitly
identified BS date to Gregorian format for the JSON output.
Do not assume every Nepali date is BS solely because the document is
in Nepali. Determine the calendar system from the document context.
If the document contains both Nepali and English versions of the
same field, use the information that is explicitly associated with
that field and use the English/Latin representation when the
document explicitly provides it.
doc_type, full_name, date_of_birth, and id_number must never be null.
Every genuine identity document contains this information somewhere
— search the full text carefully before concluding a required field
is truly absent. In the rare case one is genuinely not present
anywhere in the text after a careful search, use the empty string ""
for that field rather than null, and lower confidence_score
accordingly to reflect the incomplete extraction.
nationality and expiry_date, and only these two fields, may be null.
If either is not present anywhere in the text, set it to the JSON
value null (not the string "null", not an empty string "", not
"N/A" — the literal JSON null, with no quotes around it). Never omit
either key; both must always appear in the output, with either a real
value or null.
confidence_score is your own estimate, 0-100, of how confident you
are in the overall accuracy of the extracted fields above (not the
OCR transcription itself — assume the input text is already final).
Lower the confidence score when Nepali text is ambiguous, OCR text is
incomplete or unclear, date-calendar interpretation is uncertain,
or a required field cannot be confidently identified.

Respond with ONLY a JSON object, no other text, no markdown fences, in
exactly this shape:

{
"doc_type": <string, never null>,
"full_name": <string, never null>,
"date_of_birth": <string "YYYY-MM-DD", never null>,
"id_number": <string, never null>,
"nationality": <string or null>,
"expiry_date": <string "YYYY-MM-DD" or null>,
"confidence_score": <integer 0-100>
}

Example:

Input text:
"PASSPORT
Surname: SMITH
Given Names: JOHN WILLIAM
Date of Birth: 15 JAN 1990
Passport No: P1234567
Nationality: BRITISH
Date of Expiry: 20 MAR 2030"

Expected output:
{
"doc_type": "passport",
"full_name": "JOHN WILLIAM SMITH",
"date_of_birth": "1990-01-15",
"id_number": "P1234567",
"nationality": "BRITISH",
"expiry_date": "2030-03-20",
"confidence_score": 95
}

Nepali document example:

Input text:
"नेपाल सरकार
नागरिकता प्रमाणपत्र
नाम: राम बहादुर थापा
जन्म मिति: २०५०/०५/१५
नागरिकता नं.: १२-३४-५६-००१२३
राष्ट्रियता: नेपाली"

Expected output:
{
"doc_type": "citizenship",
"full_name": "राम बहादुर थापा",
"date_of_birth": "<converted Gregorian date>",
"id_number": "12-34-56-00123",
"nationality": "नेपाली",
"expiry_date": null,
"confidence_score": 95
}

Now extract the fields from this text:

{raw_text}
"""

BASE_DIR=os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR="output"
CHUNK_SIZE = 1024 * 1024