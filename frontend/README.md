# Foodbase Frontend

Vite frontend for the Foodbase discovery flow.

## Local setup

1. Copy `.env.example` to `.env.local`.
2. Set `VITE_API_BASE_URL=http://127.0.0.1:8000/api` unless your backend runs elsewhere.
3. Run `npm install`.
4. Run `npm run dev`.

The current frontend supports:

- Landing
- Discover
- Supplier profile
- Compare
- AI product creator
- AI supplier team

The AI routes require `FOODBASE_GROQ_API_KEY` in `backend/.env`.
