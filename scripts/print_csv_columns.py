
import csv

FILE_PATH = 'data/production/realtime_pdf_confirmed_rows.csv'

def print_columns():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            print("--- COLUMNS FOUND ---")
            for i, h in enumerate(headers):
                print(f"{i}: {h}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print_columns()
