# Upgrade Guide — v20.0

## Steps
1. **DB migration**
   ```bash
   python scripts/migrate_v20.py ./ae.db
   ```
2. **Enable router** (FastAPI)
   ```python
   from .routes import interactions
   app.include_router(interactions.router)
   ```
3. **Use V20 Pass-2 findings prompt**:
   - `prompts/7panel_pass2_findings_v20.md`

## Notes
- No files deleted. Superseded items live in `archive/superseded/`.
- Contracts:
  - `contracts/findings_v20.contract.md`
  - `contracts/relational_analysis.contract.md`
  - `contracts/rule_interactions_api.contract.md`