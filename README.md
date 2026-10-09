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


## V1.6: Light inputs + quick verdict + offer sensitivity

- The dark navy shell remains; input, dropdown, text and number fields are now light blue-gray with dark text.
- Research shows a *preliminary* BRRRR and Fix & Flip financial result after the primary property assumptions and evidence selectors. The report remains in the Investment Decision tab.
- Investment Decision contains a hypothetical offer slider and separate financial sensitivity charts. Sliding it never changes the deal input or previously saved snapshots.
- No new Streamlit secrets, database migrations or third-party requests are required for this update.
- For best usability, reload the browser after the Streamlit redeployment to refresh CSS.


## V1.7 — Guided workflow

The previous five-tab interface is replaced by a six-stage guided workflow at the top of the page:

1. Property — address lookup and base assumptions.
2. Comparable evidence — verify sale/rental comps and filter geographic candidates.
3. Renovation — line-item rehab and schedule.
4. Financing & operations — loans, vacancy, holding and selling costs.
5. Investment decision — explanation cards, what-if offers, scores, stress tests.
6. Save / export — private Supabase snapshots and JSON/Excel exports.

Navigate with the stage selector or Back / Continue buttons. Sidebar deal thresholds stay available. No database schema changes or credentials required. Importantly, selections and analyzed numbers persist within the same Streamlit session; this is not a substitute for Save / Export.

Deploy: back up your working repo, unzip the V1.7 patch at repository root, run `python -m pytest -q`, then commit `app.py core/workflow.py tests/test_workflow.py README.md` and push to `main`.


## V1.8 — Safer lookup-to-underwriting

- New address lookup clears prior property-specific asking price, ARV, rent and confidence flags; other rehab/financing preferences are retained.
- Auto-populates unit type only when confidently identified; auto-populates rent only when supplied by RentCast and labels it unverified.
- Never uses `lastSalePrice` as current asking price. An asking price is imported only if explicitly provided by the property response.
- Provider value AVM appears separately; it **never silently becomes renovated ARV**. You may deliberately adopt it as an *unverified* starting assumption.
- First session starts with empty/zero subject prices, preventing misleading sample deal scores. The investment preview waits for price and ARV.
- Re-searching the same address keeps your manually edited underwriting fields.
- No database schema or secrets changes. Tests in `tests/test_property_import.py`.

## V1.9 — Renovated ARV scenario evidence and itemized rehab
- Step 2: conservative/base/optimistic indications use only rows with **Use**, **Renovated confirmed**, a user-confirmed *closed/recorded sale date type*, a valid sold price/date, and eligible size/bedroom/radius filters. At least 3 eligible comps are required. Imported RentCast AVM listing activity **never qualifies automatically**.
- Indicators are 20th/50th/80th percentiles of simplistic size-scaled verified comparables; they are NOT appraisals or probability intervals. An analyst must explicitly select and apply one to projected ARV.
- Step 3: choose Quick category budget (existing behavior) or Detailed scope estimate (editable quantity, units, materials rate, contractor labor rate, DIY labor hours and labor method). Example rates are templates, **not Cleveland-specific real-time cost quotes**. Quantities default to zero to prevent misleading totals.
- Detailed rehab cash estimate is adopted only with **Apply detailed cash budget**, and the model adds contingency/permits separately. DIY time value is only economic comparison; not added to cash budget.
- No changes to external API requests, credentials, schema migrations or stored Supabase deal shape. Existing version 1.8 snapshots remain readable.
- Update: upload ZIP, run `git status` and `git pull origin main` if clean, unzip, run `python -m pytest -q`, then commit `app.py core/arv_range.py core/rehab_estimator.py tests/test_v19.py README.md` and push to `main`.
- For an audit: the existing quick category budget still drives rehab unless the detailed estimate is deliberately applied. The upgraded evidence UI is still analyst-driven; do not represent this as automatically verified rehab or ARV.
