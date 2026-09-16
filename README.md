# Secure Cloud-Based Question-Paper Management System

The original question paper is encrypted using **AES-256-GCM**. The AES key is divided into **five Shamir shares using a 3-of-5 threshold** and stored in multiple clouds. At release time, the required shares are reconstructed to recover the AES key, and the question paper is decrypted only for authorized release.

A secure web-based system for creating, encrypting, storing, and controlled release of competitive examination question papers.

## Technologies Used

### Frontend
- React.js
- Vite
- JavaScript
- CSS

### Backend
- Python
- Flask
- REST API

### Security
- AES-256-GCM Encryption
- Shamir Secret Sharing (3-of-5)
- Role-Based Access Control (RBAC)
- Firebase Authentication
- Audit Logging

### Cloud Services
- **Firebase** — Authentication
- **MongoDB Atlas** — Database, user roles, question-paper metadata, secret shares, and audit logs
- **Backblaze B2** — Encrypted question papers and secret shares
- **Netlify** — Frontend deployment
- **Render** — Backend deployment

## Environment Variables

### Frontend
```env
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_STORAGE_BUCKET=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
VITE_FIREBASE_MEASUREMENT_ID=
VITE_API_BASE_URL=
```

### Backend
```env
MONGO_URI=
DATABASE_NAME=
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_BUCKET_NAME=
FIREBASE_SERVICE_ACCOUNT=
```

> Do not commit `.env` files, Firebase service-account files, or secret keys to GitHub. Configure them through environment variables in the deployment platform.

## System Flow

```text
Question Setter
       ↓
Upload Question Paper
       ↓
AES-256-GCM Encryption
       ↓
Generate 5 Shamir Shares
       ↓
3-of-5 Threshold Secret Sharing
       ↓
Distribute Encrypted Data and Shares
       ↓
MongoDB Atlas + Backblaze B2
       ↓
Schedule Release Time (IST)
       ↓
Examiner Authentication
       ↓
RBAC Verification
       ↓
Release Controller
       ↓
Collect Required Shares
       ↓
Shamir Secret Reconstruction
       ↓
Recover AES Key
       ↓
AES-256-GCM Decryption
       ↓
Secure PDF Release
```

## Cloud Architecture

```text
                    ┌───────────────────┐
                    │  React + Vite     │
                    │     Netlify       │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Flask Backend   │
                    │      Render       │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌────────────┐  ┌──────────────┐  ┌──────────────┐
       │  Firebase  │  │ MongoDB Atlas │  │ Backblaze B2 │
       │    Auth    │  │   Database    │  │   Storage    │
       └────────────┘  └──────────────┘  └──────────────┘
```

## Main Features

- Secure question-paper upload
- AES-256-GCM encryption
- Shamir 3-of-5 secret sharing
- Multi-cloud storage
- Firebase authentication
- Setter and Examiner role management
- Scheduled question-paper release
- IST-based release-time control
- Secure key reconstruction
- In-memory decryption
- Audit logging
- Authorized PDF viewing

## Project Structure

```text
secure-question-paper/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── lib/
│   ├── App.jsx
│   ├── main.jsx
│   └── styles.css
│
├── backend/
│   ├── routes/
│   ├── services/
│   ├── security/
│   ├── tests/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
│
├── index.html
├── package.json
├── .gitignore
└── README.md
```

## Security Model

The question paper is encrypted before cloud storage using **AES-256-GCM**. The encryption key is split into five shares using **Shamir Secret Sharing** with a **3-of-5 threshold**.

At the scheduled release time, an authenticated examiner with the required role can reconstruct the AES key using the required shares. The encrypted question paper is then decrypted in memory and released as a PDF.

## Roles

### Question Setter
- Upload question papers
- Set examination release time
- Encrypt and securely store question papers

### Examiner
- Authenticate using Firebase
- Access authorized question papers
- Release/view papers after the scheduled release time

## Status

Working academic project implementing secure question-paper encryption, Shamir secret sharing, multi-cloud storage, authentication, role-based access control, scheduled release, key reconstruction, and secure PDF release.
