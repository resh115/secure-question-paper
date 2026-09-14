# Secure Question Paper Management System — Backend

Simple academic implementation of the cloud-based question-paper protection methodology.

## Architecture

- Firebase Authentication — identity/login
- MongoDB Atlas — application data, audit logs, and Shamir shares 1–3
- Backblaze B2 — encrypted question paper and Shamir shares 4–5
- AES-256-GCM — question-paper encryption
- Shamir 3-of-5 — AES key protection
- Flask — backend API
- RBAC — admin / setter / examiner
- Time-based release — prevents early release
- Audit logging — records security events

## Setup

1. Create a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your existing MongoDB and Backblaze values.

4. Firebase Admin:
   - In Firebase Console, use the `secure-question-paper` project.
   - Create/download a Firebase Admin SDK service-account JSON.
   - Put its path in `FIREBASE_SERVICE_ACCOUNT`.
   - Do NOT commit the JSON file.

5. Test cloud connections:

```bash
python tests/test_mongodb.py
python tests/test_backblaze.py
python tests/test_crypto.py
```

6. Start the backend:

```bash
python app.py
```

## Roles

The backend expects the Firebase UID to be mapped to an application role in MongoDB.

After a Firebase user exists:

```bash
python seed_user.py FIREBASE_UID setter
```

Use `admin`, `setter`, or `examiner`.

## Upload

Authenticated setter/admin clients send:

```http
POST /api/question-papers/upload
Authorization: Bearer FIREBASE_ID_TOKEN
Content-Type: multipart/form-data

file=<question-paper.pdf>
```

The backend encrypts the file, creates 5 Shamir shares, stores shares 1–3 in MongoDB, and stores the encrypted paper plus shares 4–5 in Backblaze.

## Release

Authenticated admin/examiner clients use:

```http
POST /api/release/<paper_id>
Authorization: Bearer FIREBASE_ID_TOKEN
```

The plaintext is decrypted in backend memory and returned to the authorized client. It is not stored back in cloud storage.

## Important

This is a simplified academic project. With a 3-of-5 threshold and only two storage locations, one location necessarily contains at least three shares. A production design would distribute the shares across at least three independent locations.
