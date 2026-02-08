# app/scripts/add_indexes.py
import sqlite3
from pathlib import Path

DB_PATH = Path("app/db/data.db")

def add_optimized_indexes():
    """
    Add optimized composite indexes for API query patterns.
    
    These indexes match the exact WHERE clauses used in the API,
    dramatically improving query performance.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Adding optimised indexes...")
    
    # =====================================================
    # FX RATES OPTIMISED INDEXES
    # =====================================================
    
    # Most common query: get latest rate for a currency pair
    # Query: WHERE base_currency = ? AND target_currency = ? AND date = ?
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fx_rates_lookup 
        ON fx_rates(base_currency, target_currency, date)
    """)
    print("✓ Created idx_fx_rates_lookup (base, target, date)")
    
    # For getting max/min dates efficiently
    # Query: SELECT MAX(date) FROM fx_rates
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fx_rates_date_desc 
        ON fx_rates(date DESC)
    """)
    print("✓ Created idx_fx_rates_date_desc")
    
    # For year-based queries with LIKE
    # Query: WHERE date LIKE '2023%'
    # Note: The existing idx_fx_date already helps here
    
    # =====================================================
    # CPI DATA OPTIMIZED INDEXES
    # =====================================================
    
    # Most common query: get CPI for specific country and year
    # Query: WHERE country_code = ? AND year = ?
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cpi_lookup 
        ON cpi_data(country_code, year)
    """)
    print("✓ Created idx_cpi_lookup (country, year)")
    
    # For year range queries (historical averages)
    # Query: WHERE country_code = ? AND year BETWEEN ? AND ?
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cpi_year_range 
        ON cpi_data(country_code, year DESC)
    """)
    print("✓ Created idx_cpi_year_range")
    
    # For getting latest CPI efficiently
    # Query: WHERE country_code = ? ORDER BY year DESC LIMIT 1
    # (idx_cpi_year_range already covers this)
    
    conn.commit()
    
    # Show statistics
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='fx_rates'
        ORDER BY name
    """)
    fx_indexes = cursor.fetchall()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='cpi_data'
        ORDER BY name
    """)
    cpi_indexes = cursor.fetchall()
    
    print("\n" + "="*60)
    print("FX Rates Indexes:")
    for idx in fx_indexes:
        print(f"  - {idx[0]}")
    
    print("\nCPI Data Indexes:")
    for idx in cpi_indexes:
        print(f"  - {idx[0]}")
    
    # Show table sizes
    cursor.execute("SELECT COUNT(*) FROM fx_rates")
    fx_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cpi_data")
    cpi_count = cursor.fetchone()[0]
    
    print(f"\nTable Statistics:")
    print(f"  FX Rates: {fx_count:,} rows")
    print(f"  CPI Data: {cpi_count:,} rows")
    print("="*60)
    
    conn.close()
    print("\n✅ All indexes created successfully!")
    
if __name__ == "__main__":
    add_optimized_indexes()