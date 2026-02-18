
import csv

FILE_PATH = 'data/production/realtime_pdf_confirmed_rows.csv'

def find_keys():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            first_row = next(reader)
            keys = list(first_row.keys())
            
            targets = ['row_content', 'environment', 'outcome', 'mechanism', 'significance']
            
            print(f"Total keys: {len(keys)}")
            
            for target in targets:
                if target in keys:
                    print(f"FOUND EXACT: '{target}'")
                else:
                    print(f"MISSING: '{target}'")
                    # Find similar
                    matching = [k for k in keys if target in k]
                    if matching:
                        print(f"  Did you mean: {matching}?")
                    else:
                        print("  No substring match found.")
                        
            # Print first 5 keys to check for BOM or weirdness
            print("\nFirst 5 keys:")
            print(keys[:5])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_keys()
