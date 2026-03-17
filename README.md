# CSV Contact List Cleaner

A Python tool that merges multiple messy CSV files into one clean, 
deduplicated contact list.

## What it does

- Combines multiple CSV files from different sources into a single output file
- Automatically detects and standardises common column name variations 
  (e.g. "e-mail", "email_address", "mail" → "email")
- Cleans and normalises values (removes junk whitespace, null-like values, 
  wrapping quotes)
- Validates email addresses and skips invalid ones
- Formats UK phone numbers to a consistent format (handles +44, 44xxxxxxxxxx)
- Removes duplicate entries by email address
- Outputs a clean combined_clean.csv with standardised columns: name, email, phone

## Example

Input — three messy CSVs with inconsistent headers and dirty data:

| Full Name       | E-Mail Address        | Mobile Number |
|-----------------|-----------------------|---------------|
| John Smith      | " john@example.com "  | +447911123456 |
| Jane Doe        | jane@example.com      | 07922234567   |
| John Smith      | john@example.com      | n/a           |

Output — one clean, deduplicated CSV:

| name       | email             | phone       |
|------------|-------------------|-------------|
| John Smith | john@example.com  | 07911123456 |
| Jane Doe   | jane@example.com  | 07922234567 |

## Usage

1. Create an `input_csvfiles` folder in the same directory as the script
2. Drop all your CSV files into it
3. Run the script:

    python csv_cleaner.py

4. Find your cleaned data in `combined_clean.csv`

## Requirements

Python 3.x — no external libraries required, uses only the standard library.

## Supported column name variations

| Field | Recognised headers |
|-------|--------------------|
| name  | full_name, full name, customer_name, contact_name |
| email | e-mail, email_address, email address, mail |
| phone | phone_number, mobile, telephone, tel, home_phone |
