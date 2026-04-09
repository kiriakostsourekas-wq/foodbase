# Foodbase Frontend

Vite frontend for the Foodbase discovery flow.

## Local setup

1. Copy `.env.example` to `.env.local`.
2. Keep `VITE_API_BASE_URL=/api` for the default local setup. Vite proxies that path to `http://127.0.0.1:8000`.
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
