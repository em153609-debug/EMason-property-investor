# EMason Property Investor — v1.0

Public, mobile-friendly Streamlit underwriting for Cleveland-area single-family through fourplex properties. Evaluates BRRRR and Fix & Flip separately, with transparent category scores, constraints, offers, scenarios, downloadable Excel + JSON snapshot reports, optional RentCast lookups, and optional private Supabase snapshot storage.

## Deploy
1. Upload all files to `main` in the GitHub repository, preserving directories (or upload the ZIP using GitHub Codespaces and unzip).
2. Streamlit Community Cloud: repository `em153609-debug/EMason-property-investor`, branch `main`, entrypoint `app.py`.
3. In Streamlit app settings → Secrets, add `RENTCAST_API_KEY`, `SUPABASE_URL`, and `SUPABASE_PUBLISHABLE_KEY`. Leave keys blank for manual-only mode.
4. Supabase SQL Editor: run `database/migrations/001_create_deals.sql`. Under Authentication → Users → Add user, create your own email/password account. Confirm email if required.
5. Never commit `.streamlit/secrets.toml` or database passwords, keys or authentication tokens.

## Modeling notes
- Purchase financing modeled as interest-only during estimated renovation+marketing months; all rehab assumed paid from cash.
- Refinancing modeled using ARV × LTV less outstanding original acquisition principal and estimated refinance fees. Lender seasoning/appraisal/DSCR/eligibility not automatically verified.
- Cash recovery is returned cash divided by peak cash investment. If refinance proceeds are negative, the deficiency increases remaining cash required.
- Cash flow includes rent vacancy; maintenance, CapEx, management, taxes, insurance, other expenses, and refinance mortgage payment.
- Flip profit is pre-tax ARV less all-in cost and selling costs.
- Financial score is rubric-based; verdict requires hard thresholds. Data evidence verification is manual and flagged distinctly.
- RentCast data retrieval is triggered explicitly to avoid surprise usage and cached for 24 hours per query. Public deployment can still experience abusive calls; introduce per-user quotas and provider caps before wide promotion.
- Private deals are isolated by Supabase user ID and row-level security; partner-shared workspaces are not part of v1.0.

## Testing
`python -m pytest tests -q`

## Release safety
Use feature branches + pull requests. Before schema changes export database content and review migration. Keep historical JSON exports for critical deals.


## Version 1.1 — Comparable evidence workbench

- Adds manually reviewed renovated sold comps and rent comps directly inside **Property & Comps**.
- Records amounts, square footage, bedroom count, date, condition verification and inclusion choice.
- Excludes unsuitable comps and explains exclusions; reports count and conservative confidence.
- Uses simple square-foot adjustment for verified renovated sold comps, median advertised rent for rentals. These are indications, not appraisals or confirmed achievable rent.
- Adds prominent verification warnings to the Deal Verdict and stores entered comp rows within JSON/Supabase analysis snapshots.
- Does **not** change financial calculation thresholds or existing Supabase database schema.

### Upgrade from 1.0

Copy the new `app.py`, `core/comps.py`, `tests/test_comps.py`, and this README into your existing GitHub repository, preserving directories. Commit to `main`; Streamlit automatically redeploys. **Do not** delete your Supabase project or rerun migrations unnecessarily. API secrets remain in Streamlit, not this repository.

For a safer rollout, first create a `v1.1-comps` Git branch and deploy a Streamlit test app from that branch. Confirm the finance calculations, comparable inputs, saving and Excel export before merging into `main`.

This version still relies on manual review for high-quality comp data. It does not automatically source all renovated sales, adjust for condition or proximity, and does not establish lender-eligible ARV.


## V1.3 (address-first UI)
- Single search action beside the address bar pulls RentCast property + value/rent comparable candidates.
- Search works with supported **US** addresses, not just Cleveland.
- Candidate comp rows merge without replacing verified edits on the same subject; switch addresses to clear prior-subject rows.
- Search is button-triggered, caches for 24 hours, and never automatically accepts unverified comps.
- Refreshed layout and clearer comparable/decision displays.
- No Supabase database changes required.


## V1.4 — Visual refresh and comparable screening controls
- Modern slate/navy/teal theme, prominent strategy scorecards, cleaner tab labels and spacing, progress indicators, and simplified decision hierarchy.
- Search remains address-first; supports RentCast-covered U.S. addresses, not Cleveland-only.
- Choose 0.5–10 mile radius and 3–24 month age windows in comparable workbench. These are LOCAL screening controls on candidates RentCast returned, NOT API geographic search parameters.
- Distance derives from source coordinates if both the subject and comp have them; otherwise remains unknown. Toggle strict filtering to exclude unknown-distance candidates. Analyst-entered mileage may also be reviewed.
- Imported listing activity date is NOT a verified sold closing date. Renovation verification and comp inclusion remain explicit.
- No Supabase migration, API key rotation, or database clearing. Saved deal schema unchanged.

### Update procedure
Upload this update ZIP into the existing Codespace, ensure `git status` shows no uncommitted tracked changes, then unzip into the project root. Run `python -m pytest -q`. Commit only the updated source files from the release ZIP. Do not commit the ZIP, API credentials or `.streamlit/secrets.toml`.


## V1.5 — dark contrast, explanations and real geographic comp search
- Dark navy UI, bright contrasting input controls, consistent dark theme for desktop/mobile.
- Three-column summary of strengths, risks and verifications in Investment Decision, with existing detailed category expanders preserved.
- Optional **Search additional nearby sold records and rental listings** in Research. Uses RentCast `GET /properties` with `address`, `radius`, `saleDateRange`, and `GET /listings/rental/long-term` with `address`, `radius`. Two additional API requests per distinct set of query parameters, cached 24 hours.
- Sale results are reported past sale records but not proof of renovated condition; rental data is asking rent not executed leases. Both import unselected. Confirm individual comps before use.
- No changes to Supabase schema, stored deal ownership, keys or Secrets.
- A live API and Streamlit-hosted smoke test must be completed after deployment.
