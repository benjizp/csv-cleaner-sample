# csv cleaner refined

import csv, os, re
from typing import Dict, List, Optional, Tuple

INPUT_FOLDER = 'input_csvfiles'
OUTPUT_FILE = 'combined_clean.csv'
REQUIRED = ['email', 'name', 'phone']

SYNONYMS = {
    # email
    "e-mail": "email",
    "email_address": "email",
    "email address": "email",
    "e-mail_address": "email",
    "e-mail address": "email",
    "mail": "email",
    "email_addr": "email",      # <-- important for "email addr"
    "emailaddr": "email",

    # name
    "full_name": "name",
    "full name": "name",
    "customer_name": "name",
    "customer name": "name",
    "contact_name": "name",
    "contact name": "name",

    # phone
    "phone_number": "phone",
    "phone number": "phone",
    "phone_no": "phone",
    "phone no": "phone",
    "mobile": "phone",
    "mobile_number": "phone",
    "mobile number": "phone",
    "home_phone": "phone",      # <-- important for "Home Phone"
    "home phone": "phone",
    "telephone": "phone",
    "tel": "phone",
    "number": "phone",
}

# use a set for fast lookup + include common dash variants
NULL_LIKE = {
    '', 'n/a', 'na', 'null', 'none', '-', 'nan',
    '—', '–'
}

def normalize_header(h: str) -> str:
    h = str(h).strip().lower()
    h = h.replace(' ', '_')
    h = h.replace('.', '')
    h = h.replace('#', '')
    return SYNONYMS.get(h, h)

def strip_wrapping_quotes(s: str) -> str:
    '''
    Removes wrapping quotes repeatedly:
    '"  hello  "' -> hello
    """hello""" -> hello
    '''
    s = s.strip()
    while len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1].strip()
    return s

def clean_value(val: object, col: str) -> str:
    if val is None:
        return ''

    s = str(val)

    # normalize weird whitespace
    s = s.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').strip()

    # remove wrapper quotes like "  NONE  " or ' email@x.com '
    s = strip_wrapping_quotes(s)

    if col == 'email':
        # remove ALL whitespace inside emails + lowercase
        s = re.sub(r'\s+', '', s).lower()
        s = s.strip('<>').strip()  # handles <email@x.com>
    else:
        # collapse multiple spaces to one
        s = ' '.join(s.split())

    if s.lower() in NULL_LIKE:
        return ''

    return s

def clean_phone(val: object) -> str:
    s = clean_value(val, 'phone')
    if not s:
        return ''

    # keep only digits
    digits = re.sub(r'\D', '', s)

    # convert +44 / 44xxxxxxxxxx to 0xxxxxxxxxx for UK mobiles (44 + 10 digits)
    if digits.startswith('44') and len(digits) == 12 and digits[2] == '7':
        digits = '0' + digits[2:]

    return digits

def build_mapping(fieldnames: List[str]) -> Dict[str, str]:
    normalized = [normalize_header(h) for h in fieldnames]
    mapping: Dict[str, str] = {}

    for original, normed in zip(fieldnames, normalized):
        if normed in REQUIRED and normed not in mapping:
            mapping[normed] = original
    return mapping

def row_key(clean_row: Dict[str, str]) -> Tuple:
    # you skip invalid/missing emails anyway, so email-only dedupe is perfect here
    return ('email', clean_row['email'])

def looks_like_email(s: str) -> bool:
    s = s.strip()
    if not s:
        return False
    if s.count('@') != 1:
        return False
    local, domain = s.split('@')
    if not local or not domain:
        return False
    if '.' not in domain:
        return False
    if any(c.isspace() for c in s):
        return False
    return True

def main() -> None:
    files_processed = 0
    rows_read = 0
    rows_written = 0
    rows_skipped_empty = 0
    dupes_removed = 0
    rows_skipped_invalid_email = 0

    seen = set()
    output_rows: List[Dict[str, str]] = []

    for filename in os.listdir(INPUT_FOLDER):
        if not filename.lower().endswith('.csv'):
            continue

        path = os.path.join(INPUT_FOLDER, filename)
        files_processed += 1

        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue

            mapping = build_mapping(reader.fieldnames)

            for row in reader:
                rows_read += 1
                clean_row: Dict[str, str] = {}

                for col in REQUIRED:
                    original_key: Optional[str] = mapping.get(col)

                    if not original_key:
                        clean_row[col] = ''
                        continue

                    if col == 'phone':
                        clean_row[col] = clean_phone(row.get(original_key, ''))
                    else:
                        clean_row[col] = clean_value(row.get(original_key, ''), col)

                if all(clean_row[c] == '' for c in REQUIRED):
                    rows_skipped_empty += 1
                    continue

                if not looks_like_email(clean_row['email']):
                    rows_skipped_invalid_email += 1
                    continue

                key = row_key(clean_row)
                if key in seen:
                    dupes_removed += 1
                    continue
                seen.add(key)

                output_rows.append(clean_row)
                rows_written += 1

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f'Processed {files_processed} files')
    print(f'Read {rows_read} rows')
    print(f'Wrote {rows_written} rows')
    print(f'Skipped {rows_skipped_empty} empty')
    print(f'Removed {dupes_removed} duplicates')
    print(f'Skipped {rows_skipped_invalid_email} invalid email')

if __name__ == '__main__':
    if not os.path.isdir(INPUT_FOLDER):
        raise SystemExit(f'Input folder not found: {INPUT_FOLDER}')
    main()
