import pandas as pd
import numpy as np
import re
from typing import Optional, List
from datetime import datetime

class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the DataCleaner with a raw dataframe.
        
        Args:
            df (pd.DataFrame): The raw input dataframe.
        """
        self.raw_df = df.copy()
        self.clean_df = df.copy()
        self.log: List[str] = []
        self.start_timestamp = datetime.now()
        self.end_timestamp = None

    def clean_all(self) -> pd.DataFrame:
        """
        Runs the full data cleaning pipeline.
        
        Order of operations is critical:
        1. Standardize text (Names, Emails)
        2. Deduplicate (now that text is standard)
        3. Fix Types (Dates)
        4. Handle Missing Values
        
        Returns:
            pd.DataFrame: The cleaned dataframe.
        """
        self.standardize_names()
        self.fix_emails()
        self.remove_duplicates()  # Run AFTER standardization for better matching
        self.clean_dates()
        self.handle_missing_values()
        self.end_timestamp = datetime.now()
        return self.clean_df

    def remove_duplicates(self) -> None:
        """Removes duplicates based on Email and Name."""
        initial_count = len(self.clean_df)
        
        # Drop strict duplicates
        self.clean_df = self.clean_df.drop_duplicates()
        
        # Drop duplicates based on Email, keeping the first
        # normalize email for check but don't modify the column yet (already done in fix_emails usually, but safe to do here)
        if 'Email' in self.clean_df.columns:
            # We assume emails are already lowercased by fix_emails, but let's be safe
            temp_email = self.clean_df['Email'].astype(str).str.lower()
            self.clean_df = self.clean_df[~temp_email.duplicated(keep='first')]

        final_count = len(self.clean_df)
        self.log.append(f"Removed {initial_count - final_count} duplicate rows.")

    def standardize_names(self) -> None:
        """Converts names to Title Case."""
        if 'Name' in self.clean_df.columns:
            self.clean_df['Name'] = self.clean_df['Name'].astype(str).str.title()
            self.log.append("Standardized Names to Title Case.")

    def fix_emails(self) -> None:
        """Fixes invalid email formats or drops them."""
        if 'Email' not in self.clean_df.columns:
            return
            
        def clean_email(email: str) -> Optional[str]:
            if pd.isna(email): return None
            email = str(email).lower().strip()
            # Simple fix: replace ' at ' with '@'
            email = email.replace(" at ", "@")
            # Basic regex validation
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return None # Invalid
            return email
            
        self.clean_df['Email'] = self.clean_df['Email'].apply(clean_email)
        
        # Drop rows where email became None
        n_before = len(self.clean_df)
        self.clean_df = self.clean_df.dropna(subset=['Email'])
        n_dropped = n_before - len(self.clean_df)
        
        self.log.append(f"Fixed email formatting. Removed {n_dropped} invalid emails.")

    def clean_dates(self) -> None:
        """Standardizes Join_Date to datetime objects."""
        if 'Join_Date' not in self.clean_df.columns:
            return

        # Coerce errors will turn 'Unknown' or bad formats into NaT
        self.clean_df['Join_Date'] = pd.to_datetime(self.clean_df['Join_Date'], errors='coerce')
        
        # Fill NaT with mode
        # Create a copy of the series to avoid SettingWithCopy warning potential
        join_dates = self.clean_df['Join_Date'].copy()
        n_fixed = join_dates.isna().sum()
        
        if n_fixed > 0 and not join_dates.mode().empty:
            mode_date = join_dates.mode()[0]
            join_dates = join_dates.fillna(mode_date)
            self.clean_df['Join_Date'] = join_dates
            self.log.append(f"Standardized Dates. Imputed {n_fixed} missing/bad dates with mode.")
        else:
             self.log.append("Standardized Dates. No missing values found or mode undefined.")

    def handle_missing_values(self) -> None:
        """Fills missing numeric values."""
        if 'Event_Attendance' in self.clean_df.columns:
            n_att = self.clean_df['Event_Attendance'].isna().sum()
            self.clean_df['Event_Attendance'] = self.clean_df['Event_Attendance'].fillna(0)
            self.log.append(f"Filled {n_att} missing Attendance records with 0.")

if __name__ == "__main__":
    # Test script to run locally
    import sys
    import os
    
    data_path = "../data/messy_club_data.csv"
    if not os.path.exists(data_path):
        print("Data file not found. Run generator first.")
        # Attempt to find it relative to current script if running from utils/
        if os.path.exists("../../data/messy_club_data.csv"):
             data_path = "../../data/messy_club_data.csv"
        else:
             sys.exit(1)
        
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Original Data Shape: {df.shape}")
    
    print("Running Cleaner...")
    cleaner = DataCleaner(df)
    clean_df = cleaner.clean_all()
    
    print("\n--- Cleaning Report ---")
    for msg in cleaner.log:
        print(msg)
        
    print(f"\nFinal Data Shape: {clean_df.shape}")
    print("Sample:\n", clean_df.head())
