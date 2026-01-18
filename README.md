# AE<->AF Wiring Patch — Option 2
Ports: Source-of-truth in `contracts/ports.json`.

Run from repo root:

```bash
bash tools/apply_chatgpt_patch.sh
```

This script:
- backs up modified files under `_archive/chatgpt_patch_<UTC>/`
- appends a defensive pipeline bridge to `app/tasks/pipeline.py`
- patches `app/cli/article_eater_contract_cli.py` to attempt to call the bridge
- runs `install_ae_envkit.sh` and `doctor.sh` if present

Then run:

```bash
./bin/article_eater eat --in contracts/ae_af/examples/input_bundle_minimal --out /tmp/ae_out_example --profile standard --hitl auto
```
