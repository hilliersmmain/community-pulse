import pandas as pd
import numpy as np
import re
import logging
from typing import Optional, List
from difflib import SequenceMatcher
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

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
        
        # Track metrics for data health score
        self.initial_record_count = len(df)
        self.duplicate_count = 0
        self.invalid_email_count = 0
        self.missing_value_count = 0
        
        logger.info(f"DataCleaner initialized with {self.initial_record_count} records")
    
    def fuzzy_match_names(self, name1: str, name2: str, threshold: float = config.FUZZY_MATCH_THRESHOLD) -> bool:
        """
        Return True if names are similar enough to be duplicates.
        
        Uses SequenceMatcher (Python's difflib) which implements a similar algorithm
        to Levenshtein distance. It calculates the ratio of matching characters
        between two strings.
        
        Args:
            name1: First name to compare
            name2: Second name to compare
            threshold: Similarity threshold (range: 0.0 to 1.0, where 1.0 is exact match).
                      Default is 0.85 (85% similarity)
        
        Returns:
            bool: True if names are similar enough to be considered duplicates
            
        Example:
            >>> fuzzy_match_names("John Smith", "Jon Smith")
            True  # 94% similarity
            >>> fuzzy_match_names("John Smith", "Jane Doe")
            False  # 30% similarity
        """
        if pd.isna(name1) or pd.isna(name2):
            return False
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio() >= threshold

    def clean_all(self) -> pd.DataFrame:
        """
        Runs the full data cleaning pipeline.
        
        Order of operations is critical:
        1. Validate schema
        2. Standardize text (Names, Emails)
        3. Deduplicate (now that text is standard, including fuzzy matching)
        4. Fix Types (Dates)
        5. Handle Missing Values
        
        Returns:
            pd.DataFrame: The cleaned dataframe.
        """
        logger.info("Starting full data cleaning pipeline...")
        self.validate_schema()
        self.standardize_names()
        self.fix_emails()
        self.remove_duplicates()  # Run AFTER standardization for better matching
        self.remove_fuzzy_duplicates()  # Additional fuzzy matching step
        self.clean_dates()
        self.handle_missing_values()
        logger.info(f"Cleaning pipeline completed. {len(self.clean_df)} records remaining.")
        return self.clean_df
    
    def validate_schema(self) -> None:
        """Validates that required columns exist in the dataframe."""
        required_columns = ['Name', 'Email']
        missing_columns = [col for col in required_columns if col not in self.clean_df.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns: {', '.join(missing_columns)}"
            logger.error(error_msg)
            self.log.append(f"ERROR: {error_msg}")
            raise ValueError(error_msg)
        
        logger.info("Schema validation passed")
        self.log.append("Schema validation passed - all required columns present.")

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
        self.duplicate_count = initial_count - final_count
        logger.info(f"Removed {self.duplicate_count} duplicate rows")
        self.log.append(f"Removed {self.duplicate_count} duplicate rows.")
    
    def remove_fuzzy_duplicates(self) -> None:
        """
        Removes near-duplicate names using fuzzy matching.
        
        Note: This uses O(n²) complexity with nested loops. For datasets under 10,000
        records, performance is acceptable. For larger datasets, consider using
        blocking techniques or indexing strategies for optimization.
        """
        if 'Name' not in self.clean_df.columns or 'Email' not in self.clean_df.columns:
            return
        
        initial_count = len(self.clean_df)
        to_drop = []
        
        # Convert to list for faster iteration
        names = self.clean_df['Name'].tolist()
        emails = self.clean_df['Email'].tolist()
        
        # Compare each name with subsequent names
        for i in range(len(names)):
            if i in to_drop:
                continue
            for j in range(i + 1, len(names)):
                if j in to_drop:
                    continue
                # Only check fuzzy match if emails are different
                # (same emails are already handled by remove_duplicates)
                if emails[i] != emails[j] and self.fuzzy_match_names(names[i], names[j]):
                    to_drop.append(j)
                    logger.debug(f"Fuzzy match found: '{names[i]}' ~ '{names[j]}'")
        
        # Drop the identified near-duplicates
        if to_drop:
            self.clean_df = self.clean_df.drop(self.clean_df.index[to_drop])
            self.clean_df = self.clean_df.reset_index(drop=True)
        
        final_count = len(self.clean_df)
        fuzzy_removed = initial_count - final_count
        
        if fuzzy_removed > 0:
            logger.info(f"Removed {fuzzy_removed} fuzzy duplicate names")
            self.log.append(f"Removed {fuzzy_removed} near-duplicate names using fuzzy matching.")

    def standardize_names(self) -> None:
        """Converts names to Title Case."""
        if 'Name' in self.clean_df.columns:
            self.clean_df['Name'] = self.clean_df['Name'].astype(str).str.title()
            logger.info("Standardized names to Title Case")
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
            if not re.match(config.EMAIL_REGEX_PATTERN, email):
                return None # Invalid
            return email
            
        self.clean_df['Email'] = self.clean_df['Email'].apply(clean_email)
        
        # Drop rows where email became None
        n_before = len(self.clean_df)
        self.clean_df = self.clean_df.dropna(subset=['Email'])
        n_dropped = n_before - len(self.clean_df)
        self.invalid_email_count = n_dropped
        
        logger.info(f"Fixed email formatting. Removed {n_dropped} invalid emails")
        self.log.append(f"Fixed email formatting. Removed {n_dropped} invalid emails.")

    def clean_dates(self) -> None:
        """Standardizes Join_Date to datetime objects and detects future dates."""
        if 'Join_Date' not in self.clean_df.columns:
            return

        # Coerce errors will turn 'Unknown' or bad formats into NaT
        self.clean_df['Join_Date'] = pd.to_datetime(self.clean_df['Join_Date'], errors='coerce')
        
        # Detect and handle future dates
        today = pd.Timestamp.now()
        future_dates = self.clean_df['Join_Date'] > today
        future_count = future_dates.sum()
        if future_count > 0:
            logger.warning(f"Found {future_count} future dates - setting to NaT")
            self.clean_df.loc[future_dates, 'Join_Date'] = pd.NaT
        
        # Fill NaT with mode
        # Create a copy of the series to avoid SettingWithCopy warning potential
        join_dates = self.clean_df['Join_Date'].copy()
        n_fixed = join_dates.isna().sum()
        
        if n_fixed > 0 and not join_dates.mode().empty:
            mode_date = join_dates.mode()[0]
            join_dates = join_dates.fillna(mode_date)
            self.clean_df['Join_Date'] = join_dates
            logger.info(f"Standardized dates. Imputed {n_fixed} missing/bad dates with mode")
            self.log.append(f"Standardized Dates. Imputed {n_fixed} missing/bad dates with mode.")
        else:
            logger.info("Standardized dates. No missing values found or mode undefined")
            self.log.append("Standardized Dates. No missing values found or mode undefined.")

    def handle_missing_values(self) -> None:
        """Fills missing numeric values."""
        if 'Event_Attendance' in self.clean_df.columns:
            n_att = self.clean_df['Event_Attendance'].isna().sum()
            self.clean_df['Event_Attendance'] = self.clean_df['Event_Attendance'].fillna(0)
            self.missing_value_count += n_att
            logger.info(f"Filled {n_att} missing Attendance records with 0")
            self.log.append(f"Filled {n_att} missing Attendance records with 0.")
    
    def calculate_data_health_score(self) -> float:
        """
        Calculate the overall data health score based on cleaning metrics.
        
        Returns:
            float: Data health score (0-100)
        """
        if self.initial_record_count == 0:
            return 100.0
        
        duplicate_rate = (self.duplicate_count / self.initial_record_count) * 100
        invalid_email_rate = (self.invalid_email_count / self.initial_record_count) * 100
        missing_rate = (self.missing_value_count / self.initial_record_count) * 100
        
        # Score = 100 - (sum of all quality issues)
        health_score = max(0, 100 - (duplicate_rate + invalid_email_rate + missing_rate))
        
        logger.info(f"Data health score calculated: {health_score:.1f}%")
        return health_score
    
    def get_cleaning_metrics(self) -> dict:
        """
        Get detailed metrics about the cleaning process.
        
        Returns:
            dict: Dictionary containing cleaning metrics
        """
        metrics = {
            'initial_records': self.initial_record_count,
            'final_records': len(self.clean_df),
            'duplicates_removed': self.duplicate_count,
            'invalid_emails_removed': self.invalid_email_count,
            'missing_values_filled': self.missing_value_count,
            'duplicate_rate': (self.duplicate_count / self.initial_record_count * 100) if self.initial_record_count > 0 else 0,
            'invalid_email_rate': (self.invalid_email_count / self.initial_record_count * 100) if self.initial_record_count > 0 else 0,
            'missing_rate': (self.missing_value_count / self.initial_record_count * 100) if self.initial_record_count > 0 else 0,
            'data_health_score': self.calculate_data_health_score()
        }
        return metrics

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
