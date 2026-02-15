"""
Helper functions to access World Bank CPI data from SQLite database.

These functions provide a clean interface to query CPI data without
needing to write SQL directly.
"""

import sqlite3
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path
from functools import lru_cache


# Default database path
DB_PATH = Path("app/db/data.db")


@lru_cache(maxsize=256)
def get_latest_cpi(country_code: str, db_path: str = None) -> Optional[float]:
    if db_path is None:
        db_path = DB_PATH

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cpi_value FROM cpi_data
        WHERE country_code = ?
          AND cpi_value IS NOT NULL
        ORDER BY year DESC
        LIMIT 1
    """, (country_code.upper(),))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None



def get_cpi_for_year(country_code: str, year: int, db_path: str = None) -> Optional[float]:
    """
    Get CPI value for a specific country and year.
    
    Args:
        country_code: ISO 3-letter country code
        year: Year (e.g., 2023)
        db_path: Path to database (optional)
    
    Returns:
        CPI value for that year, or None if not found
    
    Example:
        >>> get_cpi_for_year('AUS', 2020)
        120.81
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cpi_value FROM cpi_data
        WHERE country_code = ? AND year = ?
          AND cpi_value IS NOT NULL
    """, (country_code.upper(), year))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None


@lru_cache(maxsize=512)
def get_historical_average_cpi(country_code: str, years: int = 20, db_path: str = None) -> Optional[float]:
    """
    Get average CPI over the last N years.
    
    Args:
        country_code: ISO 3-letter country code
        years: Number of years to average (default: 20)
        db_path: Path to database (optional)
    
    Returns:
        Average CPI value, or None if insufficient data
    
    Example:
        >>> get_historical_average_cpi('AUS', 20)
        105.47
    
    Note: Results are cached for performance.
    """
    if db_path is None:
        db_path = DB_PATH
    
    end_year = datetime.now().year - 1  # CPI data typically lags by 1 year
    start_year = end_year - years + 1
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT AVG(cpi_value) FROM cpi_data
        WHERE country_code = ? AND year BETWEEN ? AND ?
    """, (country_code.upper(), start_year, end_year))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] else None


def get_cpi_time_series(country_code: str, start_year: int = None, end_year: int = None, 
                        db_path: str = None) -> List[Dict]:
    """
    Get complete CPI time series for a country.
    
    Args:
        country_code: ISO 3-letter country code
        start_year: Starting year (optional, defaults to earliest available)
        end_year: Ending year (optional, defaults to latest available)
        db_path: Path to database (optional)
    
    Returns:
        List of dictionaries with 'year' and 'cpi_value' keys
    
    Example:
        >>> data = get_cpi_time_series('AUS', 2020, 2023)
        >>> for row in data:
        ...     print(f"{row['year']}: {row['cpi_value']:.2f}")
        2020: 120.81
        2021: 124.27
        2022: 132.47
        2023: 139.88
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()
    
    if start_year and end_year:
        cursor.execute("""
            SELECT year, cpi_value FROM cpi_data
            WHERE country_code = ? AND year BETWEEN ? AND ?
            ORDER BY year ASC
        """, (country_code.upper(), start_year, end_year))
    elif start_year:
        cursor.execute("""
            SELECT year, cpi_value FROM cpi_data
            WHERE country_code = ? AND year >= ?
            ORDER BY year ASC
        """, (country_code.upper(), start_year))
    elif end_year:
        cursor.execute("""
            SELECT year, cpi_value FROM cpi_data
            WHERE country_code = ? AND year <= ?
            ORDER BY year ASC
        """, (country_code.upper(), end_year))
    else:
        cursor.execute("""
            SELECT year, cpi_value FROM cpi_data
            WHERE country_code = ?
            ORDER BY year ASC
        """, (country_code.upper(),))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def get_available_countries(db_path: str = None) -> List[Dict]:
    """
    Get list of all countries with CPI data.
    
    Args:
        db_path: Path to database (optional)
    
    Returns:
        List of dictionaries with country info
    
    Example:
        >>> countries = get_available_countries()
        >>> print(f"Found {len(countries)} countries")
        >>> print(countries[0])
        {'code': 'ABW', 'name': 'Aruba', 'years_of_data': 45, 'earliest_year': 1980, 'latest_year': 2024}
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            country_code as code,
            country_name as name,
            COUNT(*) as years_of_data,
            MIN(year) as earliest_year,
            MAX(year) as latest_year
        FROM cpi_data
        GROUP BY country_code, country_name
        ORDER BY country_code
    """)
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def get_country_name(country_code: str, db_path: str = None) -> Optional[str]:
    """
    Get the full country name from country code.
    
    Args:
        country_code: ISO 3-letter country code
        db_path: Path to database (optional)
    
    Returns:
        Country name, or None if not found
    
    Example:
        >>> get_country_name('AUS')
        'Australia'
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT country_name FROM cpi_data
        WHERE country_code = ?
        LIMIT 1
    """, (country_code.upper(),))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None


def search_countries(query: str, db_path: str = None) -> List[Dict]:
    """
    Search for countries by name or code.
    
    Args:
        query: Search term (matches country name or code)
        db_path: Path to database (optional)
    
    Returns:
        List of matching countries
    
    Example:
        >>> results = search_countries('Austral')
        >>> for country in results:
        ...     print(f"{country['code']}: {country['name']}")
        AUS: Australia
        AUT: Austria
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_pattern = f"%{query}%"
    cursor.execute("""
        SELECT DISTINCT
            country_code as code,
            country_name as name,
            COUNT(*) as years_of_data
        FROM cpi_data
        WHERE country_name LIKE ? OR country_code LIKE ?
        GROUP BY country_code, country_name
        ORDER BY country_name
    """, (search_pattern, search_pattern.upper()))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def get_database_stats(db_path: str = None) -> Dict:
    """
    Get statistics about the CPI database.
    
    Args:
        db_path: Path to database (optional)
    
    Returns:
        Dictionary with database statistics
    
    Example:
        >>> stats = get_database_stats()
        >>> print(f"Countries: {stats['total_countries']}")
        >>> print(f"Records: {stats['total_records']}")
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total countries
    cursor.execute("SELECT COUNT(DISTINCT country_code) FROM cpi_data")
    total_countries = cursor.fetchone()[0]
    
    # Total records
    cursor.execute("SELECT COUNT(*) FROM cpi_data")
    total_records = cursor.fetchone()[0]
    
    # Year range
    cursor.execute("SELECT MIN(year), MAX(year) FROM cpi_data")
    min_year, max_year = cursor.fetchone()
    
    # Last updated
    cursor.execute("SELECT MAX(last_updated) FROM cpi_data")
    last_updated = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_countries': total_countries,
        'total_records': total_records,
        'earliest_year': min_year,
        'latest_year': max_year,
        'last_updated': last_updated,
        'database_path': str(db_path)
    }


# Example usage and testing
if __name__ == "__main__":
    print("="*60)
    print("World Bank CPI Data - Helper Functions Test")
    print("="*60)
    
    # Database stats
    stats = get_database_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Total countries: {stats['total_countries']}")
    print(f"  Total records: {stats['total_records']}")
    print(f"  Year range: {stats['earliest_year']} - {stats['latest_year']}")
    print(f"  Last updated: {stats['last_updated']}")
    
    # Test Australia
    print(f"\nAustralia (AUS):")
    print(f"  Latest CPI: {get_latest_cpi('AUS'):.2f}")
    print(f"  CPI in 2020: {get_cpi_for_year('AUS', 2020):.2f}")
    print(f"  20-year average: {get_historical_average_cpi('AUS', 20):.2f}")
    
    # Test USA
    print(f"\nUSA:")
    print(f"  Latest CPI: {get_latest_cpi('USA'):.2f}")
    print(f"  20-year average: {get_historical_average_cpi('USA', 20):.2f}")
    
    # Search example
    print(f"\nSearch for 'Japan':")
    results = search_countries('Japan')
    for country in results:
        print(f"  {country['code']}: {country['name']} ({country['years_of_data']} years)")
    
    # Time series example
    print(f"\nAustralia CPI 2020-2024:")
    data = get_cpi_time_series('AUS', 2020, 2024)
    for row in data:
        print(f"  {row['year']}: {row['cpi_value']:.2f}")
