# AE↔AF Contract Additions

This overlay adds the missing executable entrypoint:

- `app/cli/article_eater_contract_cli.py`

Your repo may already contain the normative contract pack at:

- `contracts/ae_af/schemas/`
- `contracts/ae_af/examples/`

After applying this overlay, rerun your installer:

```bash
bash install_ae_envkit.sh
bash doctor.sh
```

Then smoke test:

```bash
./bin/article_eater eat --in contracts/ae_af/examples/input_bundle_minimal --out /tmp/ae_out_example --profile standard --hitl auto
```
