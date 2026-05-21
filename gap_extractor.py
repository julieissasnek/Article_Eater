import sys
import subprocess

args = sys.argv[1:]
templates_dir = "data/templates"

if "--templates" in args:
    idx = args.index("--templates")
    if idx + 1 < len(args):
        raw_path = args[idx + 1]
        if "Article_Eater/" in raw_path:
            templates_dir = raw_path.replace("Article_Eater/", "")
        else:
            templates_dir = raw_path

cmd = ["python3", "voi_gap_extractor.py", "--input-dir", templates_dir, "--output", "data/prioritized_gaps_manifest.json"]
cmd_string = " ".join(cmd)
print(f"Wrapper redirecting to: {cmd_string}")
subprocess.run(cmd)
