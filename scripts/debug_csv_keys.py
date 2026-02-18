
import csv

FILE_PATH = 'data/production/realtime_pdf_confirmed_rows.csv'

def debug_keys():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            first_row = next(reader)
            print("--- KEYS IN DICTREADER ---")
            for key in first_row.keys():
                print(f"'{key}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_keys()
