
import csv

FILE_PATH = 'data/production/realtime_pdf_confirmed_rows.csv'

def list_keys():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            first_row = next(reader)
            keys = list(first_row.keys())
            print("--- ALL KEYS ---")
            for i, k in enumerate(keys):
                print(f"{i}: {k}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_keys()
