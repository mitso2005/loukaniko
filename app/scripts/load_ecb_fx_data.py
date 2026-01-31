"""
Load and update EUR FX data from ECB (European Central Bank).

This script:
1. Loads historical EUR FX data from CSV (1999-01-04 to present)
2. Stores it in SQLite database
3. Provides daily update function to fetch latest rates
4. Handles EUR-base conversions (EUR->USD->JPY, etc.)

Usage:
    # Initial load from CSV
    python load_ecb_fx_data.py eurofxref-hist.csv
    
    # Daily update (fetch latest rates from API)
    python load_ecb_fx_data.py --update
"""

import sqlite3
import csv
import requests
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def init_fx_database(db_path: str = "data.db"):
    """Create FX rates table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fx_rates (
            date TEXT NOT NULL,
            base_currency TEXT NOT NULL,
            target_currency TEXT NOT NULL,
            rate REAL NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (date, base_currency, target_currency)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fx_date ON fx_rates(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fx_pair ON fx_rates(base_currency, target_currency)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fx_base ON fx_rates(base_currency)")
    
    conn.commit()
    conn.close()
    print("✓ FX database initialized")


def load_ecb_csv(csv_path: str, db_path: str = "data.db"):
    """
    Load ECB EUR FX historical data from CSV.
    
    The CSV format is:
    Date,USD,JPY,BGN,CZK,...
    2026-01-30,1.1919,183.59,N/A,24.325,...
    
    This stores EUR as base currency.
    """
    print(f"Loading ECB FX data from {csv_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Get all currency columns (everything except Date)
        currencies = [col for col in reader.fieldnames if col != 'Date']
        
        records_count = 0
        dates_processed = 0
        
        for row in reader:
            date = row['Date']
            dates_processed += 1
            
            # Store EUR to each currency
            for currency in currencies:
                rate_str = row[currency]
                
                # Skip N/A values
                if rate_str == 'N/A' or not rate_str.strip():
                    continue
                
                try:
                    rate = float(rate_str)
                    
                    # Insert EUR -> Currency rate
                    cursor.execute("""
                        INSERT OR REPLACE INTO fx_rates 
                        (date, base_currency, target_currency, rate, last_updated)
                        VALUES (?, ?, ?, ?, ?)
                    """, (date, 'EUR', currency, rate, datetime.now()))
                    
                    records_count += 1
                    
                except ValueError:
                    continue
        
        # Also add EUR -> EUR = 1.0 for each date
        cursor.execute("SELECT DISTINCT date FROM fx_rates WHERE base_currency = 'EUR'")
        dates = [row[0] for row in cursor.fetchall()]
        
        for date in dates:
            cursor.execute("""
                INSERT OR REPLACE INTO fx_rates 
                (date, base_currency, target_currency, rate, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (date, 'EUR', 'EUR', 1.0, datetime.now()))
        
        conn.commit()
        
        print(f"\n✅ Successfully loaded EUR FX data:")
        print(f"   - Dates processed: {dates_processed}")
        print(f"   - Total FX records: {records_count}")
        print(f"   - Database: {db_path}")
    
    conn.close()


def update_latest_rates(db_path: str = "data.db", api_url: str = None):
    """
    Fetch latest EUR FX rates from Frankfurter API and update database.
    
    This should be run daily to keep the database up to date.
    """
    if api_url is None:
        api_url = "https://api.frankfurter.app/latest"
    
    print("Fetching latest EUR FX rates from API...")
    
    try:
        response = requests.get(api_url, params={"base": "EUR"})
        response.raise_for_status()
        data = response.json()
        
        date = data['date']
        rates = data['rates']
        
        print(f"✓ Received data for {date}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if we already have this date
        cursor.execute("""
            SELECT COUNT(*) FROM fx_rates 
            WHERE date = ? AND base_currency = 'EUR'
        """, (date,))
        
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"⚠️  Data for {date} already exists. Updating...")
        
        # Insert/update rates
        records_updated = 0
        for currency, rate in rates.items():
            cursor.execute("""
                INSERT OR REPLACE INTO fx_rates 
                (date, base_currency, target_currency, rate, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (date, 'EUR', currency, rate, datetime.now()))
            records_updated += 1
        
        # Add EUR -> EUR = 1.0
        cursor.execute("""
            INSERT OR REPLACE INTO fx_rates 
            (date, base_currency, target_currency, rate, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (date, 'EUR', 'EUR', 1.0, datetime.now()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Updated {records_updated} rates for {date}")
        
    except Exception as e:
        print(f"❌ Error updating rates: {e}")
        raise


def verify_data(db_path: str = "data.db"):
    """Verify the loaded FX data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("FX DATA VERIFICATION")
    print("="*60)
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM fx_rates")
    total_records = cursor.fetchone()[0]
    print(f"\nTotal FX records: {total_records:,}")
    
    # Count currencies
    cursor.execute("SELECT COUNT(DISTINCT target_currency) FROM fx_rates WHERE base_currency = 'EUR'")
    currency_count = cursor.fetchone()[0]
    print(f"Currencies available: {currency_count}")
    
    # Date range
    cursor.execute("SELECT MIN(date), MAX(date) FROM fx_rates")
    min_date, max_date = cursor.fetchone()
    print(f"Date range: {min_date} to {max_date}")
    
    # Latest rates sample
    cursor.execute("""
        SELECT target_currency, rate 
        FROM fx_rates 
        WHERE base_currency = 'EUR' AND date = ?
        ORDER BY target_currency
        LIMIT 10
    """, (max_date,))
    
    print(f"\nSample - Latest EUR rates ({max_date}):")
    for currency, rate in cursor.fetchall():
        print(f"  EUR/{currency}: {rate}")
    
    # Count by base currency
    cursor.execute("""
        SELECT base_currency, COUNT(*) as count
        FROM fx_rates
        GROUP BY base_currency
    """)
    
    print("\nRecords by base currency:")
    for base, count in cursor.fetchall():
        print(f"  {base}: {count:,} records")
    
    conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load and update EUR FX data")
    parser.add_argument("csv_file", nargs='?', help="CSV file to load (eurofxref-hist.csv)")
    parser.add_argument("--update", action="store_true", help="Fetch and update latest rates")
    parser.add_argument("--db", default="data.db", help="Database path")
    
    args = parser.parse_args()
    
    # Initialize database
    init_fx_database(args.db)
    
    if args.update:
        # Daily update mode
        update_latest_rates(args.db)
        verify_data(args.db)
    
    elif args.csv_file:
        # Load from CSV
        csv_path = Path(args.csv_file)
        if not csv_path.exists():
            print(f"Error: File not found: {csv_path}")
            sys.exit(1)
        
        load_ecb_csv(str(csv_path), args.db)
        verify_data(args.db)
    
    else:
        # Try to find the CSV file
        possible_files = [
            "eurofxref-hist.csv",
            Path.cwd() / "eurofxref-hist.csv",
        ]
        
        csv_file = None
        for f in possible_files:
            if Path(f).exists():
                csv_file = f
                break
        
        if csv_file:
            print(f"Found CSV file: {csv_file}")
            load_ecb_csv(str(csv_file), args.db)
            verify_data(args.db)
        else:
            print("Usage:")
            print("  Load from CSV:   python load_ecb_fx_data.py eurofxref-hist.csv")
            print("  Daily update:    python load_ecb_fx_data.py --update")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ COMPLETE - FX data ready!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Use the helper functions to query FX data")
    print("  2. Run --update daily to keep data current")
    print("  3. Integrate with your travel value calculator")
