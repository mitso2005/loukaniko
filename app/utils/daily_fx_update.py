"""
Daily FX rate updater.

Run this script every morning to fetch latest EUR FX rates.
"""

import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))

from app.scripts.load_ecb_fx_data import update_latest_rates

if __name__ == "__main__":
    print("Starting daily FX update...")

    # Database path
    db_path = root / "app" / "db" / "data.db"

    try:
        update_latest_rates(str(db_path))
        print("✅ FX rates updated successfully!")
    except Exception as e:
        print(f"❌ Error updating FX rates: {e}")