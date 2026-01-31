"""
Load World Bank CPI Excel/CSV data into SQLite database.

This script:
1. Reads the World Bank CPI data file
2. Parses the data structure (skips metadata rows)
3. Stores it in a normalized SQLite database
4. Creates indexes for fast lookups

Usage:
    python load_world_bank_cpi.py path/to/excel_file.xls
    python load_world_bank_cpi.py path/to/csv_file.csv
"""

import sqlite3
import csv
import sys
from pathlib import Path
from datetime import datetime


def load_world_bank_cpi_from_csv(csv_path: str, db_path: str = "market_data.db"):
    """
    Load World Bank CPI data from CSV into SQLite database.
    
    Args:
        csv_path: Path to the CSV file
        db_path: Path to SQLite database (default: market_data.db)
    """
    print(f"Loading World Bank CPI data from {csv_path}...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cpi_data (
            country_code TEXT NOT NULL,
            year INTEGER NOT NULL,
            cpi_value REAL NOT NULL,
            country_name TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (country_code, year)
        )
    """)
    
    # Create index for faster lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cpi_country ON cpi_data(country_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cpi_year ON cpi_data(year)")
    
    # Read CSV file
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Skip metadata rows (first 3 rows)
        next(reader)  # Data Source
        next(reader)  # Last Updated Date
        next(reader)  # Empty row
        
        # Read header row to get years
        header = next(reader)
        # Header: Country Name, Country Code, Indicator Name, Indicator Code, 1960, 1961, ...
        years = [int(year) for year in header[4:] if year.strip()]
        
        print(f"Found data for years: {years[0]} to {years[-1]}")
        
        # Process each country
        countries_processed = 0
        total_records = 0
        
        for row in reader:
            if len(row) < 4:
                continue
            
            country_name = row[0].strip()
            country_code = row[1].strip()
            
            if not country_code:
                continue
            
            # Process CPI values for each year
            for i, year in enumerate(years):
                # CPI values start at index 4 in the row
                cpi_value_str = row[4 + i] if (4 + i) < len(row) else ""
                
                if cpi_value_str and cpi_value_str.strip():
                    try:
                        cpi_value = float(cpi_value_str)
                        
                        # Insert into database
                        cursor.execute("""
                            INSERT OR REPLACE INTO cpi_data 
                            (country_code, year, cpi_value, country_name, last_updated)
                            VALUES (?, ?, ?, ?, ?)
                        """, (country_code, year, cpi_value, country_name, datetime.now()))
                        
                        total_records += 1
                    except ValueError:
                        # Skip invalid values
                        pass
            
            countries_processed += 1
        
        conn.commit()
        
        print(f"\n✅ Successfully loaded data:")
        print(f"   - Countries processed: {countries_processed}")
        print(f"   - Total CPI records: {total_records}")
        print(f"   - Database: {db_path}")
    
    conn.close()


def verify_data(db_path: str = "market_data.db"):
    """Verify the loaded data with some sample queries."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("DATA VERIFICATION")
    print("="*60)
    
    # Count countries
    cursor.execute("SELECT COUNT(DISTINCT country_code) FROM cpi_data")
    country_count = cursor.fetchone()[0]
    print(f"\nTotal countries: {country_count}")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM cpi_data")
    record_count = cursor.fetchone()[0]
    print(f"Total CPI records: {record_count}")
    
    # Year range
    cursor.execute("SELECT MIN(year), MAX(year) FROM cpi_data")
    min_year, max_year = cursor.fetchone()
    print(f"Year range: {min_year} to {max_year}")
    
    # Sample: Australia's latest CPI
    cursor.execute("""
        SELECT year, cpi_value 
        FROM cpi_data 
        WHERE country_code = 'AUS' 
        ORDER BY year DESC 
        LIMIT 5
    """)
    print("\nSample - Australia's latest CPI values:")
    for year, cpi in cursor.fetchall():
        print(f"  {year}: {cpi:.2f}")
    
    # Sample: USA's latest CPI
    cursor.execute("""
        SELECT year, cpi_value 
        FROM cpi_data 
        WHERE country_code = 'USA' 
        ORDER BY year DESC 
        LIMIT 5
    """)
    print("\nSample - USA's latest CPI values:")
    for year, cpi in cursor.fetchall():
        print(f"  {year}: {cpi:.2f}")
    
    # Countries with most data
    cursor.execute("""
        SELECT country_code, country_name, COUNT(*) as years
        FROM cpi_data
        GROUP BY country_code
        ORDER BY years DESC
        LIMIT 5
    """)
    print("\nCountries with most historical data:")
    for code, name, years in cursor.fetchall():
        print(f"  {code} ({name}): {years} years")
    
    conn.close()


if __name__ == "__main__":
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Look for the file in current directory
        csv_file = Path("API_FP_CPI_TOTL_DS2_en_excel_v2_219.csv")
        xls_file = Path("API_FP_CPI_TOTL_DS2_en_excel_v2_219.xls")
        
        if csv_file.exists():
            input_file = str(csv_file)
        elif xls_file.exists():
            print("XLS file found. Converting to CSV first...")
            import subprocess
            subprocess.run([
                "libreoffice", "--headless", "--convert-to", "csv",
                str(xls_file)
            ], check=True)
            input_file = str(csv_file)
        else:
            print("Error: No input file found.")
            print("Usage: python load_world_bank_cpi.py path/to/file.csv")
            sys.exit(1)
    
    # Convert XLS to CSV if needed
    input_path = Path(input_file)
    if input_path.suffix.lower() == '.xls':
        print("Converting XLS to CSV...")
        import subprocess
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "csv",
            str(input_path)
        ], check=True)
        input_file = str(input_path.with_suffix('.csv'))
    
    # Load the data
    load_world_bank_cpi_from_csv(input_file)
    
    # Verify the data
    verify_data()
    
    print("\n" + "="*60)
    print("✅ COMPLETE - Data ready to use!")
    print("="*60)
