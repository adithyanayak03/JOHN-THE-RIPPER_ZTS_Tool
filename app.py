# app.py
import os
import base64
import io
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from argon2 import PasswordHasher
import pyotp
import qrcode
from dotenv import load_dotenv

load_dotenv()
PEPPER = os.getenv("PEPPER", "dev-pepper-change-me")

app = Flask(__name__)
DB_URL = "sqlite:///auth_demo.db"
engine = create_engine(DB_URL, echo=False, future=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

ph = PasswordHasher()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message":"Zero Trust Auth API running"})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error":"email and password required"}), 400

    session = Session()
    if session.query(User).filter_by(email=email).first():
        session.close()
        return jsonify({"error":"user exists"}), 400

    # hash with pepper
    salted = password + PEPPER
    hash_ = ph.hash(salted)

    user = User(email=email, password_hash=hash_)
    session.add(user)
    session.commit()
    session.close()
    return jsonify({"message":"User registered successfully!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    token = data.get("token")  # optional mfa token

    if not email or not password:
        return jsonify({"error":"email and password required"}), 400

    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if not user:
        session.close()
        return jsonify({"error":"invalid credentials"}), 401

    try:
        ph.verify(user.password_hash, password + PEPPER)
    except Exception:
        session.close()
        return jsonify({"error":"invalid credentials"}), 401

    if user.mfa_enabled:
        if not token:
            session.close()
            return jsonify({"mfa_required": True, "message":"MFA token required"}), 200
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(token):
            session.close()
            return jsonify({"error":"invalid token"}), 401

    session.close()
    return jsonify({"message":"Login successful!"})

@app.route("/mfa/setup", methods=["POST"])
def mfa_setup():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error":"email required"}), 400
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if not user:
        session.close()
        return jsonify({"error":"user not found"}), 404

    secret = pyotp.random_base32()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="ZeroTrustDemo")

    # Generate QR PNG and return base64
    img = qrcode.make(uri)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    b64 = base64.b64encode(buffered.getvalue()).decode()

    # store secret temporarily (enable will set mfa_enabled)
    user.mfa_secret = secret
    session.add(user)
    session.commit()
    session.close()
    return jsonify({"secret": secret, "provisioning_uri": uri, "qr_b64": b64})

@app.route("/mfa/enable", methods=["POST"])
def mfa_enable():
    data = request.get_json() or {}
    email = data.get("email")
    token = data.get("token")
    if not email or not token:
        return jsonify({"error":"email and token required"}), 400

    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if not user or not user.mfa_secret:
        session.close()
        return jsonify({"error":"mfa not setup"}), 400

    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(token):
        session.close()
        return jsonify({"error":"invalid token"}), 401

    user.mfa_enabled = True
    session.add(user)
    session.commit()
    session.close()
    return jsonify({"message":"MFA enabled"})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
