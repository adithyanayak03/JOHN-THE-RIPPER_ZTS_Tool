# password-tool-demo (Zero Trust Auth style)

Educational demo implementing Zero Trust style authentication with Flask, Argon2id password hashing, and TOTP-based MFA.

**Important:** This repository is for learning and testing only. Do not use real user accounts or secrets. Do not test against systems you don't own.

## Features
- Register users with Argon2id-hashed passwords
- Login endpoint with optional MFA enforcement (TOTP)
- Simple SQLite + SQLAlchemy datastore
- MFA QR provisioning (returns base64 image)
- Guidance for secure configuration and deployment

## Quick start (local)
1. Clone:
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. Create virtualenv (Windows PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (do **not** commit):
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   PEPPER=ReplaceWithARandomPepperValue
   ```

5. Run:
   ```bash
   python app.py
   ```

6. Endpoints (examples):
   - `GET /` → health check
   - `POST /register` → `{ "email": "...", "password": "..." }`
   - `POST /login` → `{ "email": "...", "password": "...", "token": "..."? }`
   - `POST /mfa/setup` → generate secret & QR (base64)
   - `POST /mfa/enable` → enable MFA for user with token

## Colab
If you prefer Colab, add your notebook in `notebooks/` and link to it here:
`https://colab.research.google.com/github/<username>/<repo>/blob/main/notebooks/your_notebook.ipynb`

## File overview
- `app.py` — Flask app with endpoints
- `models.py` — SQLAlchemy models
- `requirements.txt` — Python requirements
- `.gitignore`, `LICENSE`, etc.

## Security notes
- Never commit `.env` or any secret keys.
- Use a secure PEPPER in production (store in an environment secret manager).
- Do not use Flask’s dev server in production.
- Tune Argon2 parameters for your environment.

## License
This project is for educational purpose as part of a Zero Trust Security Assignment. Feel free to use it — see `LICENSE`.
