import pandas as pd
import numpy as np
from faker import Faker
import random
import logging
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

fake = Faker()

def generate_messy_data(num_records: int = config.DEFAULT_NUM_RECORDS, save_path: Optional[str] = None) -> pd.DataFrame:
    """
    Generates a dataset with intentional 'messiness' for cleaning demonstration.
    
    Args:
        num_records: Number of base records to generate (default: 500)
        save_path: Optional file path to save the generated CSV
    
    Returns:
        pd.DataFrame: A messy dataset with duplicates, invalid emails, 
                      inconsistent formatting, and missing values
    
    Messiness includes:
    - Duplicates (approx 10%)
    - Inconsistent capitalization in Names
    - Invalid Email formats
    - Inconsistent Date formats (YYYY-MM-DD vs MM/DD/YYYY)
    - Missing values (NaN)
    """
    logger.info(f"Generating {num_records} messy records...")
    data = []
    
    # Generate base data
    for _ in range(num_records):
        # Event registration logic
        event_registered = np.random.choice(config.EVENT_CHOICES, p=config.EVENT_PROBABILITIES)
        
        # Registration date (only if registered for an event)
        if event_registered != "None" and random.random() > 0.4:
            # 60% of registered users have a registration date
            reg_date = fake.date_between(start_date='-6m', end_date='today')
        else:
            reg_date = None
        
        record = {
            "ID": fake.uuid4(),
            "Name": fake.name(),
            "Email": fake.email(),
            "Join_Date": fake.date_between(start_date='-2y', end_date='today'),
            "Last_Login": fake.date_time_between(start_date='-1y', end_date='now'),
            "Event_Attendance": np.random.randint(0, 20),
            "Role": np.random.choice(
                list(config.ROLE_PROBABILITIES.keys()), 
                p=list(config.ROLE_PROBABILITIES.values())
            ),
            "Event_Registered": event_registered,
            "Registration_Date": reg_date
        }
        data.append(record)
    
    df = pd.DataFrame(data)
    
    # --- INTRODUCE MESSINESS ---
    
    # 1. Duplicates
    num_duplicates = int(num_records * config.DUPLICATE_RATE)
    duplicates = df.sample(num_duplicates, replace=True)
    df = pd.concat([df, duplicates], ignore_index=True)
    logger.info(f"Added {num_duplicates} duplicate records")
    
    # 2. Inconsistent Names (mix of UPPER, lower, Title)
    def mess_up_name(name: str) -> str:
        r = random.random()
        if r < 0.1: return name.upper()
        if r < 0.2: return name.lower()
        return name
    df['Name'] = df['Name'].apply(mess_up_name)
    
    # 3. Invalid Emails
    def mess_up_email(email: str) -> str:
        if random.random() < config.INVALID_EMAIL_RATE:
            return email.replace("@", " at ")  # Invalid format
        return email
    df['Email'] = df['Email'].apply(mess_up_email)
    
    # 4. Inconsistent Date Formats & Types in 'Join_Date'
    # Current format is datetime.date object. Convert some to strings of different formats.
    def mess_up_date(d) -> str:
        r = random.random()
        if r < 0.1:
            return d.strftime("%m/%d/%Y")  # US format string
        if r < 0.2:
            return d.strftime("%d-%m-%Y")  # Euro format string
        if r < 0.25:
             # Random string noise
            return "Unknown" 
        return d  # Keep as object or ISO string roughly
    df['Join_Date'] = df['Join_Date'].apply(mess_up_date)

    # 5. Missing Values
    cols_to_nan = ['Event_Attendance', 'Last_Login']
    for col in cols_to_nan:
        df.loc[df.sample(frac=config.MISSING_VALUE_RATE).index, col] = np.nan

    # Shuffle dataset
    df = df.sample(frac=1).reset_index(drop=True)
    
    if save_path:
        df.to_csv(save_path, index=False)
        logger.info(f"Generated messy data at {save_path} with {len(df)} rows.")
    else:
        logger.info(f"Generated messy data with {len(df)} rows (not saved).")
        
    return df

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    import os
    if not os.path.exists("../data"):
        os.makedirs("../data", exist_ok=True)
        
    generate_messy_data(save_path="../data/messy_club_data.csv")
