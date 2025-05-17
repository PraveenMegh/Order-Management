#!/bin/bash

echo "🔄 Starting full setup for Shree Sai Industries - Order Management"

# --- Navigate to project root ---
cd "$(dirname "$0")/.."

# --- Create virtual environment if not exists ---
if [ ! -d "venv" ]; then
    echo "⚙️ Creating virtual environment..."
    python3 -m venv venv
else
    echo "✔ Using existing virtual environment."
fi

# --- Activate virtual environment ---
source venv/bin/activate

# --- Install requirements ---
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# --- Initialize Database ---
echo "🗄 Creating fresh database and tables..."
python scripts/create_db.py

# --- Seed Users (safe if already exists) ---
echo "👥 Seeding default users..."
python scripts/user_setup.py

# --- Send SMTP test email (optional check) ---
echo "📧 Sending SMTP test email..."
python scripts/smtp_test.py

echo "✅ All setup done. You can now run Streamlit app with:"
echo "streamlit run app.py"
