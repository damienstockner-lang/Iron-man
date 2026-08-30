# Iron-man / Friday Assistant

This branch adds a scaffold for the "Friday Assistant" — a personal assistant that manages schedule, steps, telephony (SMS/calls), translations, design generation, and integrations with Google/YouTube/Instagram/Snap.

This scaffold contains a minimal FastAPI backend, environment examples, architecture notes, and a telephony verification flow stub. It is intended as the starting point for iterative development. See the included issues in the repo for prioritized work.

Quick start (development)

1. Copy example.env to .env and fill in values (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER).

2. Create and activate a Python venv, then install dependencies:

   pip install -r backend/requirements.txt

3. Run the server:

   uvicorn backend.main:app --reload --port 8000

4. Open http://localhost:8000/docs to view API docs.

Notes
- This scaffold intentionally uses SQLite for prototyping and matches the DB schema from your existing PR.
- Do NOT commit real secrets. Add Twilio credentials as repository secrets or to your local .env only.
