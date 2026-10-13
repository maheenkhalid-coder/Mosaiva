import firebase_admin
from firebase_admin import credentials

from pathlib import Path

key_path = Path(__file__).resolve().parents[1] / "serviceAccountKey.json"

if not firebase_admin._apps:
    credential = credentials.Certificate(str(key_path))
    firebase_admin.initialize_app(credential)