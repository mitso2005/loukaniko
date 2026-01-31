"""
FX Helper Functions with EUR-base conversion.

Since ECB data is EUR-based, conversions between non-EUR currencies
require going through EUR (e.g., AUD -> EUR -> JPY).

Examples:
    EUR -> USD: Direct lookup
    AUD -> JPY: AUD -> EUR (1/rate) then EUR -> JPY (rate)
"""

import sqlite3
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pathlib import Path


DB_PATH = Path("app/db/data.db")


def get_latest_rate(base: str, target: str, db_path: str = None) -> Optional[float]:
    """
    Get the most recent exchange rate from base to target currency.
    
    Handles EUR-base conversion automatically:
    - EUR -> XXX: Direct lookup
    - XXX -> EUR: 1 / (EUR -> XXX)
    - XXX -> YYY: (XXX -> EUR) * (EUR -> YYY) = (1 / EUR->XXX) * (EUR->YYY)
    
    Args:
        base: Base currency code (e.g., 'AUD', 'EUR')
        target: Target currency code (e.g., 'USD', 'JPY')
        db_path: Database path (optional)
    
    Returns:
        Exchange rate, or None if not found
    
    Examples:
        >>> get_latest_rate('EUR', 'USD')
        1.1919
        >>> get_latest_rate('AUD', 'JPY')
        107.99
    """
    if db_path is None:
        db_path = DB_PATH
    
    base = base.upper()
    target = target.upper()
    
    # Same currency
    if base == target:
        return 1.0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get latest date
    cursor.execute("SELECT MAX(date) FROM fx_rates")
    latest_date = cursor.fetchone()[0]
    
    if not latest_date:
        conn.close()
        return None
    
    # Case 1: EUR -> Target (direct lookup)
    if base == 'EUR':
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE base_currency = 'EUR' AND target_currency = ? AND date = ?
        """, (target, latest_date))
        
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    # Case 2: Base -> EUR (inverse of EUR -> Base)
    elif target == 'EUR':
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE base_currency = 'EUR' AND target_currency = ? AND date = ?
        """, (base, latest_date))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return 1.0 / result[0]
        return None
    
    # Case 3: Base -> Target (via EUR)
    # Base -> Target = (Base -> EUR) * (EUR -> Target)
    #                = (1 / EUR -> Base) * (EUR -> Target)
    else:
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE base_currency = 'EUR' AND target_currency = ? AND date = ?
        """, (base, latest_date))
        eur_to_base = cursor.fetchone()
        
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE base_currency = 'EUR' AND target_currency = ? AND date = ?
        """, (target, latest_date))
        eur_to_target = cursor.fetchone()
        
        conn.close()
        
        if eur_to_base and eur_to_target and eur_to_base[0]:
            # Base -> Target = (1 / EUR -> Base) * (EUR -> Target)
            base_to_eur = 1.0 / eur_to_base[0]
            return base_to_eur * eur_to_target[0]
        
        return None


def get_rate_for_date(base: str, target: str, date: str, db_path: str = None) -> Optional[float]:
    """
    Get exchange rate for a specific date.
    
    Args:
        base: Base currency
        target: Target currency
        date: Date in YYYY-MM-DD format
        db_path: Database path (optional)
    
    Returns:
        Exchange rate for that date, or None if not found
    """
    if db_path is None:
        db_path = DB_PATH
    
    base = base.upper()
    target = target.upper()
    
    if base == target:
        return 1.0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if base == 'EUR':
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE base_currency = 'EUR' AND target_currency = ? AND date = ?
        """, (target, date))
        
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    elif target == 'EUR':
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE base_currency = 'EUR' AND target_currency = ? AND date = ?
        """, (base, date))
        
        result = cursor.fetchone()
        conn.close()
        return (1.0 / result[0]) if result and result[0] else None
    
    else:
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE base_currency = 'EUR' AND target_currency = ? AND date = ?
        """, (base, date))
        eur_to_base = cursor.fetchone()
        
        cursor.execute("""
            SELECT rate FROM fx_rates
            WHERE base_currency = 'EUR' AND target_currency = ? AND date = ?
        """, (target, date))
        eur_to_target = cursor.fetchone()
        
        conn.close()
        
        if eur_to_base and eur_to_target and eur_to_base[0]:
            return (1.0 / eur_to_base[0]) * eur_to_target[0]
        
        return None


def get_year_average_rate(base: str, target: str, year: int, db_path: str = None) -> Optional[float]:
    """
    Get average exchange rate for a specific year.
    
    Args:
        base: Base currency
        target: Target currency
        year: Year (e.g., 2023)
        db_path: Database path (optional)
    
    Returns:
        Average rate for that year, or None if insufficient data
    """
    if db_path is None:
        db_path = DB_PATH
    
    base = base.upper()
    target = target.upper()
    
    if base == target:
        return 1.0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all dates in the year
    cursor.execute("""
        SELECT DISTINCT date FROM fx_rates
        WHERE date LIKE ? || '%'
        ORDER BY date
    """, (str(year),))
    
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not dates:
        return None
    
    # Calculate average across all dates
    rates = []
    for date in dates:
        rate = get_rate_for_date(base, target, date, db_path)
        if rate is not None:
            rates.append(rate)
    
    return sum(rates) / len(rates) if rates else None


def get_historical_average_rate(base: str, target: str, years: int, db_path: str = None) -> Optional[float]:
    """
    Get average exchange rate over the last N years.
    
    Args:
        base: Base currency
        target: Target currency
        years: Number of years to average
        db_path: Database path (optional)
    
    Returns:
        Average rate over period, or None if insufficient data
    """
    end_year = datetime.now().year - 1
    start_year = end_year - years + 1
    
    yearly_averages = []
    
    for year in range(start_year, end_year + 1):
        avg = get_year_average_rate(base, target, year, db_path)
        if avg is not None:
            yearly_averages.append(avg)
    
    return sum(yearly_averages) / len(yearly_averages) if yearly_averages else None


def get_supported_currencies(db_path: str = None) -> List[str]:
    """
    Get list of all supported currencies in the database.
    
    Returns:
        List of currency codes
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT target_currency 
        FROM fx_rates 
        WHERE base_currency = 'EUR'
        ORDER BY target_currency
    """)
    
    currencies = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return currencies


def get_latest_date(db_path: str = None) -> Optional[str]:
    """Get the most recent date with FX data."""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(date) FROM fx_rates")
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None


def get_fx_stats(db_path: str = None) -> Dict:
    """Get statistics about the FX database."""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM fx_rates")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT target_currency) FROM fx_rates WHERE base_currency = 'EUR'")
    currency_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT MIN(date), MAX(date) FROM fx_rates")
    min_date, max_date = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(DISTINCT date) FROM fx_rates")
    days_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_records': total_records,
        'currencies': currency_count,
        'earliest_date': min_date,
        'latest_date': max_date,
        'days_of_data': days_count,
        'database_path': str(db_path)
    }


# Example usage and testing
if __name__ == "__main__":
    print("="*60)
    print("FX Helper Functions Test")
    print("="*60)
    
    # Database stats
    stats = get_fx_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Total records: {stats['total_records']:,}")
    print(f"  Currencies: {stats['currencies']}")
    print(f"  Date range: {stats['earliest_date']} to {stats['latest_date']}")
    print(f"  Days of data: {stats['days_of_data']:,}")
    
    # Test direct EUR conversions
    print(f"\nDirect EUR conversions (latest):")
    print(f"  EUR -> USD: {get_latest_rate('EUR', 'USD'):.4f}")
    print(f"  EUR -> JPY: {get_latest_rate('EUR', 'JPY'):.2f}")
    print(f"  EUR -> AUD: {get_latest_rate('EUR', 'AUD'):.4f}")
    
    # Test reverse conversions
    print(f"\nReverse conversions:")
    print(f"  USD -> EUR: {get_latest_rate('USD', 'EUR'):.4f}")
    print(f"  AUD -> EUR: {get_latest_rate('AUD', 'EUR'):.4f}")
    
    # Test cross-currency conversions (via EUR)
    print(f"\nCross-currency conversions (via EUR):")
    print(f"  AUD -> USD: {get_latest_rate('AUD', 'USD'):.4f}")
    print(f"  AUD -> JPY: {get_latest_rate('AUD', 'JPY'):.2f}")
    print(f"  USD -> JPY: {get_latest_rate('USD', 'JPY'):.2f}")
    print(f"  GBP -> USD: {get_latest_rate('GBP', 'USD'):.4f}")
    
    # Test historical averages
    print(f"\nHistorical averages (20 years):")
    print(f"  AUD -> USD: {get_historical_average_rate('AUD', 'USD', 20):.4f}")
    print(f"  AUD -> JPY: {get_historical_average_rate('AUD', 'JPY', 20):.2f}")
    
    # List some currencies
    currencies = get_supported_currencies()
    print(f"\nSupported currencies ({len(currencies)} total):")
    print(f"  {', '.join(currencies[:15])}, ...")
    
    print("\n" + "="*60)
    print("✅ All tests complete!")
    print("="*60)
