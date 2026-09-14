# Secure Question Paper Frontend

Advanced React + Vite frontend for the Secure Cloud-Based Question-Paper Management System.

## Stack

- React 19
- Vite
- Firebase Authentication
- Flask REST API
- Lucide React icons
- Responsive CSS with glassmorphism / security-dashboard UI

## Run locally

```powershell
npm install
copy .env.example .env.local
npm run dev
```

Set the Firebase Web SDK values in `.env.local` and keep `VITE_API_BASE_URL=http://127.0.0.1:5000` for local backend development.

The Firebase Web SDK configuration is client-side configuration; never put the Firebase Admin service-account JSON in this frontend project.

## Backend contract

- `GET /` — backend health
- `GET /api/auth/me` — authenticated user/role
- `POST /api/question-papers/upload` — setter/admin upload
- `POST /api/release/<paper_id>` — examiner/admin release

The upload form sends multipart fields `file`, `exam_name`, and `release_at`.
The release endpoint returns the decrypted PDF bytes for in-browser display.
