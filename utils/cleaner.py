import pandas as pd
import re
from typing import Optional, List
from datetime import datetime


class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        """Initialize the DataCleaner with a raw dataframe."""
        self.raw_df = df.copy()
        self.clean_df = df.copy()
        self.log: List[str] = []
        self.start_timestamp = datetime.now()
        self.end_timestamp: Optional[datetime] = None

    def clean_all(self, steps=None) -> pd.DataFrame:
        """Runs the full data cleaning pipeline or selected steps."""
        if steps is None:
            steps = ["standardize_names", "fix_emails", "remove_duplicates", "clean_dates", "handle_missing_values"]

        if "standardize_names" in steps:
            self.standardize_names()
        if "fix_emails" in steps:
            self.fix_emails()
        if "remove_duplicates" in steps:
            self.remove_duplicates()
        if "clean_dates" in steps:
            self.clean_dates()
        if "handle_missing_values" in steps:
            self.handle_missing_values()

        self.end_timestamp = datetime.now()
        return self.clean_df

    def remove_duplicates(self) -> None:
        """Removes duplicates based on Email and Name."""
        initial_count = len(self.clean_df)

        self.clean_df = self.clean_df.drop_duplicates()

        if "Email" in self.clean_df.columns:
            temp_email = self.clean_df["Email"].astype(str).str.lower()
            self.clean_df = self.clean_df[~temp_email.duplicated(keep="first")]

        final_count = len(self.clean_df)
        self.log.append(f"Removed {initial_count - final_count} duplicate rows.")

    def standardize_names(self) -> None:
        """Converts names to Title Case."""
        if "Name" in self.clean_df.columns:
            self.clean_df["Name"] = self.clean_df["Name"].astype(str).str.title()
            self.log.append("Standardized Names to Title Case.")

    def fix_emails(self) -> None:
        """Fixes invalid email formats or drops them."""
        if "Email" not in self.clean_df.columns:
            return

        def clean_email(email: str) -> Optional[str]:
            if pd.isna(email):
                return None
            email = str(email).lower().strip()
            email = email.replace(" at ", "@")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return None
            return email

        self.clean_df["Email"] = self.clean_df["Email"].apply(clean_email)

        n_before = len(self.clean_df)
        self.clean_df = self.clean_df.dropna(subset=["Email"])
        n_dropped = n_before - len(self.clean_df)

        self.log.append(f"Fixed email formatting. Removed {n_dropped} invalid emails.")

    def clean_dates(self) -> None:
        """Standardizes Join_Date to datetime objects."""
        if "Join_Date" not in self.clean_df.columns:
            return

        self.clean_df["Join_Date"] = pd.to_datetime(self.clean_df["Join_Date"], errors="coerce")

        join_dates = self.clean_df["Join_Date"].copy()
        n_fixed = join_dates.isna().sum()

        if n_fixed > 0 and not join_dates.mode().empty:
            mode_date = join_dates.mode()[0]
            join_dates = join_dates.fillna(mode_date)
            self.clean_df["Join_Date"] = join_dates
            self.log.append(f"Standardized Dates. Imputed {n_fixed} missing/bad dates with mode.")
        else:
            self.log.append("Standardized Dates. No missing values found or mode undefined.")

    def handle_missing_values(self) -> None:
        """Fills missing numeric values."""
        if "Event_Attendance" in self.clean_df.columns:
            n_att = self.clean_df["Event_Attendance"].isna().sum()
            self.clean_df["Event_Attendance"] = self.clean_df["Event_Attendance"].fillna(0)
            self.log.append(f"Filled {n_att} missing Attendance records with 0.")


if __name__ == "__main__":
    import sys
    import os

    data_path = "../data/messy_club_data.csv"
    if not os.path.exists(data_path):
        print("Data file not found. Run generator first.")
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
