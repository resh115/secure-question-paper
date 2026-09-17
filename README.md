# Secure Cloud-Based Question-Paper Management System

## DEMO VIDEO

[Watch Demo Video](https://drive.google.com/file/d/1JOhXbkSLJOIR5DoOCKBtAp0nqcXlYntM/view?usp=drive_link)

The original question paper is encrypted using **AES-256-GCM**. The AES
key is divided into **five Shamir shares using a 3-of-5 threshold** and
stored in multiple clouds. At release time, the required shares are
reconstructed to recover the AES key, and the question paper is
decrypted only for authorized release.

A secure web-based system for creating, encrypting, storing, and
controlled release of competitive examination question papers.

## Technologies / Tools Used

### Frontend

-   React.js
-   Vite
-   JavaScript
-   CSS

### Backend

-   Python
-   Flask
-   REST API

### Security

-   AES-256-GCM Encryption
-   Shamir Secret Sharing (3-of-5)
-   Role-Based Access Control (RBAC)
-   Firebase Authentication
-   Audit Logging

### Cloud Services

-   **Firebase** --- Authentication
-   **MongoDB Atlas** --- Database, users, question-paper metadata,
    secret shares, and audit logs
-   **Backblaze B2** --- Encrypted question papers and secret shares
-   **Netlify / Vercel** --- Frontend deployment
-   **Render** --- Backend deployment

## System Flow

``` text
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
Store Encrypted Paper + Shares
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

## Installation and Running

### Prerequisites

-   Node.js and npm
-   Python 3
-   Git

### Clone Repository

``` bash
git clone https://github.com/resh115/secure-question-paper.git
cd secure-question-paper
```

### Frontend Setup

``` bash
npm install
npm run dev
```

Frontend: `http://localhost:5173`

Create a root `.env` file:

``` env
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_STORAGE_BUCKET=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
VITE_FIREBASE_MEASUREMENT_ID=
VITE_API_BASE_URL=http://127.0.0.1:5000
```

### Backend Setup

Open another terminal:

``` bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

``` env
MONGO_URI=
DATABASE_NAME=
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_BUCKET_NAME=
FIREBASE_SERVICE_ACCOUNT=firebase-service-account.json
```

Place the Firebase Admin SDK service-account JSON file inside
`backend/`.

Run:

``` bash
python app.py
```

Backend: `http://127.0.0.1:5000`

## Project Structure and Modules

``` text
secure-question-paper/
├── src/
│   ├── components/       # Reusable React UI components
│   ├── pages/            # Login, Setter and Examiner dashboards
│   ├── lib/              # Firebase and API configuration
│   ├── App.jsx           # Main React application
│   └── styles.css        # Application styling
│
├── backend/
│   ├── routes/           # Flask API routes
│   ├── services/         # Encryption, Shamir, MongoDB, B2 and Firebase services
│   ├── security/         # RBAC, audit logging and time control
│   ├── tests/             # Backend verification tests
│   ├── app.py            # Flask application entry point
│   ├── config.py         # Backend configuration
│   └── requirements.txt  # Python dependencies
│
├── index.html
├── package.json
├── .gitignore
└── README.md
```

  Module                 Purpose
  ---------------------- ---------------------------------------------------
  `encryption.py`        AES-256-GCM encryption/decryption
  `shamir.py`            3-of-5 secret sharing and reconstruction
  `mongodb.py`           MongoDB Atlas connection and database operations
  `backblaze.py`         Backblaze B2 storage operations
  `firebase_auth.py`     Firebase authentication token verification
  `rbac.py`              Role-based access control
  `time_control.py`      IST-based scheduled release control
  `audit.py`             Security and activity audit logging
  `question_papers.py`   Question-paper upload and processing
  `release.py`           Authorized release, reconstruction and decryption

## Sample Input

``` text
File: mathematics_exam.pdf
Release Date: 2026-09-20
Release Time: 09:00 IST
Role: Question Setter
```

### Processing

``` text
mathematics_exam.pdf
        ↓
AES-256-GCM Encryption
        ↓
AES-256 Encryption Key
        ↓
Shamir 3-of-5 Secret Sharing
        ↓
5 Secret Shares
        ↓
Cloud Storage
```

## Sample Output

### Backend Health Check

**Input:**

``` text
GET http://127.0.0.1:5000/
```

**Output:**

``` json
{
  "status": "ok",
  "service": "Secure Question Paper Backend"
}
```

### Successful Release

``` text
Authentication       : Successful
Role Verification    : Examiner
Release Status       : Released
Share Reconstruction : Successful
AES Key Recovery     : Successful
Decryption           : Successful
Output               : Question Paper PDF
```

### Before Release Time

``` text
Release Status : Locked
Access         : Denied
Reason         : Question paper is not yet available for release
```

## Testing

From the `backend` directory:

``` powershell
$env:PYTHONPATH="."
python tests/test_mongodb.py
python tests/test_backblaze.py
python tests/test_crypto.py
```

Expected cryptographic result:

``` text
AES-256 + Shamir 3-of-5 test PASSED
```

## Security

-   Question papers are encrypted before cloud storage.
-   AES-256 keys are protected using Shamir 3-of-5 secret sharing.
-   Firebase provides authentication.
-   RBAC controls Setter and Examiner access.
-   Release is controlled using IST-based scheduling.
-   Decryption occurs only during authorized release.
-   Audit logs record security and application events.
