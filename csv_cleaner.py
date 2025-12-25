
# HOW TO USE:
# 1. Put all your messy CSV files in a folder called 'input_csvfiles'
# 2. Double-click this file
# 3. Get your clean file: 'combined_clean.csv'
#
# That's it. No installation needed.


import csv , os 
from typing import Dict, List, Optional, Tuple

INPUT_FOLDER = 'input_csvfiles'
OUTPUT_FILE = 'combined_clean.csv'
REQUIRED = ['email' , 'name' , 'phone']

# dictionary of synonyms: 
SYNONYMS = {    # email
    "e-mail": "email",
    "email_address": "email",
    "email address": "email",
    "e-mail_address": "email",
    "e-mail address": "email",
    "mail": "email",

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
    "home phone": "phone",
    "telephone": "phone",
    "tel": "phone",
    "number": "phone", }

NULL_LIKE = ('', 'n/a', 'na' , 'null' , 'none' , '-', 'nan')

# Functions which make the main loop simpler:

def normalize_header(h:str) -> str:
    h = str(h).strip().lower()
    h = h.replace(' ' , '_')
    h = h.replace('.' , '')
    h = h.replace('#' , '')
    return SYNONYMS.get(h, h)

def clean_value(val: object, col: str) -> str:
    s = '' if val is None else str(val).strip()
    if s.lower() in NULL_LIKE:
        s = ''
    if col == 'email':
        s = s.lower()
    return s

def build_mapping(fieldnames: List[str]) -> Dict[str,str]:
    normalized = [normalize_header(h) for h in fieldnames]
    mapping: Dict[str , str] = {}
    
    for original, normed in zip(fieldnames , normalized):
        if normed in REQUIRED and normed not in mapping:
            mapping[normed] = original 
    return mapping

def row_key(clean_row: Dict[str,str]) -> Tuple:
    if clean_row['email']:
        return('email' , clean_row["email"])
    return('row' , clean_row["email"], clean_row['name'] , clean_row['phone'])

def main() -> None:

    files_processed = 0
    rows_read = 0
    rows_written = 0
    rows_skipped_empty = 0
    dupes_removed = 0

    seen = set()
    output_rows: List[Dict[str, str]] = [] #List[Dict[str, str]] is just a type hint.

    for filename in os.listdir(INPUT_FOLDER):
        if not filename.lower().endswith('.csv'):
            continue

        path = os.path.join(INPUT_FOLDER , filename)
        files_processed += 1

        with open(path, newline = '', encoding = 'utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue

            mapping = build_mapping(reader.fieldnames)

            for row in reader:
                rows_read += 1
                clean_row = {}

                for col in REQUIRED:
                    original_key : Optional[str] = mapping.get(col)
                    clean_row[col] = clean_value(row.get(original_key, ''), col)

                if all(clean_row[c] == '' for c in REQUIRED):
                    rows_skipped_empty +=1
                    continue

                key = row_key(clean_row)
                if key in seen:
                    dupes_removed += 1
                    continue
                seen.add(key)

                output_rows.append(clean_row)
                rows_written += 1

    with open(OUTPUT_FILE , 'w' , newline = '', encoding ='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames = REQUIRED)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f'Processed {files_processed} files')
    print(f'Read {rows_read} rows')
    print(f'Wrote {rows_written} rows')
    print(f'Skipped {rows_skipped_empty} empty ')
    print(f'Removed {dupes_removed} duplicates')

if __name__ == '__main__':
    if not os.path.isdir(INPUT_FOLDER):
        raise SystemExit(f'Input folder not found: {INPUT_FOLDER}')
    main()