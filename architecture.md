# Architecture and roadmap

Overview
- Mobile client: React Native (iOS + Android) for cross-platform access to camera, calls, SMS, and sensors.
- Backend: FastAPI (Python) with a relational DB (SQLite for prototype, Postgres recommended for production).
- Telephony & Messaging: Twilio programmable SMS & Voice for OTP verification, outbound calls, and voicemail recording.
- Calendar: Google Calendar API integration for "what I have today" and appointment booking.
- Steps: Integrate with Google Fit / Apple HealthKit or accept manual uploads.
- Image/design generation: Use an image-generation API (OpenAI, Stability) to create designs on demand.
- Translation: Google Cloud Translate or Microsoft Translator.
- Instagram/Snap: Use official SDKs where available (Instagram Graph API, Snap Kit) — some actions require app review.

Phases
- Phase 1 (MVP): schedule CRUD, steps tracking, contacts, phone verification OTP flow, SMS sending, TTS in-app, translation API, design generation prototype, simple web/open intents for YouTube/Google.
- Phase 2: calendar sync, Twilio calls + TTS bridging (consent flow), voicemail recording & playback, health integration.
- Phase 3: Instagram/Snap deeper integrations, helmet AR / Iron-Man view, TV remote via Google Cast.

Security & Privacy
- Store PII encrypted at rest; use TLS for all transport.
- Consent screens for any call bridging or recordings; explicit opt-in required.
- Logs for actions and audit trail.

Deployment
- Start with a small VPS or managed app (Fly.io, Heroku, Render). Use managed Postgres for production.

