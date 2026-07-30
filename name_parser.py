"""
name_parser.py — Full name to components splitting
ATBU Academic Planning Portal — Phase 1 Foundation

The NUC format uses separate Last Name / First Name / Other Names columns,
but the Newly Promoted format has a single NAME field. This module
intelligently splits full names into components.

Logic:
  1. Split the name by whitespace into tokens
  2. The LAST token is the Last Name (surname/family name)
  3. The FIRST token is the First Name (given name)
  4. Everything BETWEEN first and last is Other Names (middle names)
  5. Edge cases: single-word names, titles (Jr., Sr., III),
     hyphenated names, names with multiple words in surname

Known limitations logged for user review on import.
"""

import re
from typing import Dict, Optional

# Titles and suffixes that should stay with the name, not be split off
SUFFIXES = {"jr.", "sr.", "ii", "iii", "iv", "v", "phd", "ph.d."}

# Common Nigerian name prefixes that are part of the surname
NAME_PREFIXES = {"ab", "bin", "bint", "binti", "ibn", "al", "el"}


def split_full_name(full_name: str) -> Dict[str, str]:
    """
    Split a full name string into components.
    
    Args:
        full_name: A full name like "Bose Adamu Abdullahi" or "Sale Idi"
    
    Returns:
        Dict with keys: last_name, first_name, other_names
        Example: "Bose Adamu Abdullahi" → 
                 {"last_name": "Abdullahi", "first_name": "Bose", "other_names": "Adamu"}
    
    Logic:
        Last token = Last Name
        First token = First Name
        Middle tokens = Other Names
    """
    if not full_name or not full_name.strip():
        return {"last_name": "", "first_name": "", "other_names": ""}
    
    # Clean the name
    name = full_name.strip()
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    
    tokens = name.split()
    
    if len(tokens) == 0:
        return {"last_name": "", "first_name": "", "other_names": ""}
    
    if len(tokens) == 1:
        # Single word name — treat as first name, no last name
        return {"last_name": "", "first_name": tokens[0], "other_names": ""}
    
    if len(tokens) == 2:
        # "First Last" pattern
        return {
            "last_name": tokens[1],
            "first_name": tokens[0],
            "other_names": ""
        }
    
    # 3+ tokens: "First Middle1 Middle2 ... Last"
    # Check if the last token is a known suffix (Jr., Sr., III)
    last_token = tokens[-1].lower().rstrip('.')
    if last_token in SUFFIXES:
        # The surname is the second-to-last token, suffix is appended to last name
        # E.g., "John Smith Jr." → last_name = "Smith Jr.", first_name = "John"
        last_name = f"{tokens[-2]} {tokens[-1]}"
        first_name = tokens[0]
        other_tokens = tokens[1:-2]
    else:
        # Standard case: last token = Last Name
        last_name = tokens[-1]
        first_name = tokens[0]
        other_tokens = tokens[1:-1]
    
    return {
        "last_name": last_name,
        "first_name": first_name,
        "other_names": " ".join(other_tokens) if other_tokens else ""
    }


def parse_nuc_date(date_str: str) -> str:
    """
    Normalize dates to YYYY-MM-DD format.
    
    Handles multiple formats found in the data:
      - "01-October, 2013" → "2013-10-01"
      - "2024-10-01"       → "2024-10-01" (already normalized)
      - "01-October-2013"  → "2013-10-01"
      - "October 1, 2013"  → "2013-10-01"
    
    Args:
        date_str: A date string in various formats
    
    Returns:
        Date in YYYY-MM-DD format, or the original string if parsing fails
    """
    if not date_str or not date_str.strip():
        return ""
    
    date_str = date_str.strip()
    
    # Check if already in YYYY-MM-DD format (ISO)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    
    # Check if already in YYYY-MM-DD with various separators
    if re.match(r'^\d{4}[/.]\d{2}[/.]\d{2}$', date_str.replace('-', '/')):
        parts = re.split(r'[/.-]', date_str)
        return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
    
    # Try "DD-Month, YYYY" or "DD-Month-YYYY" format (e.g., "01-October, 2013")
    month_map = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    
    # Remove commas and split
    cleaned = date_str.replace(",", "").replace("/", "-")
    parts = cleaned.split("-")
    
    if len(parts) == 3:
        # Try all 3 combinations: DD-Month-YYYY, Month-DD-YYYY, YYYY-Month-DD
        combos = [
            (parts[0], parts[1], parts[2]),  # DD-Month-YYYY
            (parts[1], parts[0], parts[2]),  # Month-DD-YYYY
            (parts[2], parts[1], parts[0]),  # YYYY-Month-DD
        ]
        for day_part, month_part, year_part in combos:
            month_lower = month_part.strip().lower()
            if month_lower in month_map:
                month_num = month_map[month_lower]
                day = day_part.strip().zfill(2)
                year = year_part.strip()
                return f"{year}-{month_num}-{day}"
    
    # Try "Month DD, YYYY" format
    match = re.match(r'([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})', date_str)
    if match:
        month_lower = match.group(1).lower()
        if month_lower in month_map:
            return f"{match.group(3)}-{month_map[month_lower]}-{match.group(2).zfill(2)}"
    
    # Try "Mon-YY" format (e.g., "Jan-25", "Oct-25")
    match = re.match(r'([A-Za-z]{3})-(\d{2,4})', date_str)
    if match:
        month_str = match.group(1).lower()
        year_str = match.group(2)
        if month_str in month_map:
            if len(year_str) == 2:
                year_str = f"20{year_str}" if int(year_str) < 50 else f"19{year_str}"
            return f"{year_str}-{month_map[month_str]}-01"
    
    # If all parsing fails, return original string (will be flagged during review)
    return date_str


def get_year_from_date(date_str: str) -> Optional[int]:
    """
    Extract the year from a date string.
    Used for year-based aggregation in charts.
    
    Args:
        date_str: A date string (preferably already normalized to YYYY-MM-DD)
    
    Returns:
        Year as integer, or None if parsing fails
    """
    if not date_str:
        return None
    
    # Try YYYY-MM-DD first
    match = re.match(r'^(\d{4})', date_str)
    if match:
        return int(match.group(1))
    
    # Fall back to parsing
    normalized = parse_nuc_date(date_str)
    if normalized and normalized != date_str:
        match = re.match(r'^(\d{4})', normalized)
        if match:
            return int(match.group(1))
    
    return None
