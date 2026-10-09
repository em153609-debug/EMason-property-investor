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
