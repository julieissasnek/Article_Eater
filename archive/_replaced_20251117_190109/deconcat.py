import sys, pathlib, re
def main(txt_path):
    data = pathlib.Path(txt_path).read_text(encoding='utf-8', errors='ignore')
    parts = re.split(r'^----- FILE PATH: ', data, flags=re.M)
    for chunk in parts[1:]:
        head, body = chunk.split('\n',1)
        rel = head.strip()
        content = body.split('----- CONTENT START -----\n',1)[1]
        content = content.rsplit('\n----- CONTENT END -----',1)[0]
        p = pathlib.Path(rel); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
    print('Reconstructed.')
if __name__=='__main__':
    if len(sys.argv)<2:
        print('Usage: python deconcat.py <concatenated.txt>'); sys.exit(1)
    main(sys.argv[1])