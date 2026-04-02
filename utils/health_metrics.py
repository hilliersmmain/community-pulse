"""Data Health Metrics Module"""

import pandas as pd
import re
from typing import Dict, Any
from datetime import datetime


class DataHealthMetrics:
    """Calculate comprehensive health metrics for a dataset."""

    def __init__(self, df: pd.DataFrame):
        """Initialize the DataHealthMetrics calculator."""
        self.df = df.copy()
        self.timestamp = datetime.now()

    def calculate_completeness_score(self) -> float:
        """Calculate the completeness score based on non-null values."""
        if self.df.empty:
            return 0.0

        total_cells = self.df.size
        non_null_cells = total_cells - self.df.isna().sum().sum()

        return (non_null_cells / total_cells) * 100

    def calculate_duplicate_score(self) -> float:
        """Calculate the duplicate score based on unique records."""
        if len(self.df) == 0:
            return 100.0

        unique_rows = len(self.df.drop_duplicates())
        total_rows = len(self.df)

        return (unique_rows / total_rows) * 100

    def calculate_formatting_score(self) -> float:
        """Calculate the formatting score based on field validity."""
        scores = []

        if "Email" in self.df.columns:
            valid_emails = self.df["Email"].apply(self._is_valid_email).sum()
            email_score = (valid_emails / len(self.df)) * 100
            scores.append(email_score)

        if "Join_Date" in self.df.columns:
            valid_dates = self._count_valid_dates("Join_Date")
            date_score = (valid_dates / len(self.df)) * 100
            scores.append(date_score)

        if "Name" in self.df.columns:
            valid_names = self.df["Name"].apply(self._is_valid_name).sum()
            name_score = (valid_names / len(self.df)) * 100
            scores.append(name_score)

        return sum(scores) / len(scores) if scores else 100.0

    def _is_valid_email(self, email: str) -> bool:
        """Check if an email is in a valid format."""
        if pd.isna(email):
            return False

        email_str = str(email).strip()
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email_str))

    def _is_valid_name(self, name: str) -> bool:
        """Check if a name is in a reasonable format."""
        if pd.isna(name):
            return False

        name_str = str(name).strip()
        pattern = r"^[a-zA-Z\s\'.-]+$"
        return bool(re.match(pattern, name_str)) and len(name_str) > 0

    def _count_valid_dates(self, column: str) -> int:
        """Count valid dates in a column."""
        try:
            parsed = pd.to_datetime(self.df[column], errors="coerce")
            return parsed.notna().sum()
        except Exception:
            return 0

    def calculate_overall_health_score(self) -> float:
        """Calculate the overall health score as a weighted average."""
        completeness = self.calculate_completeness_score()
        duplicates = self.calculate_duplicate_score()
        formatting = self.calculate_formatting_score()

        overall = (completeness * 0.4) + (duplicates * 0.3) + (formatting * 0.3)

        return round(overall, 1)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all health metrics in a single dictionary."""
        return {
            "completeness_score": round(self.calculate_completeness_score(), 1),
            "duplicate_score": round(self.calculate_duplicate_score(), 1),
            "formatting_score": round(self.calculate_formatting_score(), 1),
            "overall_score": self.calculate_overall_health_score(),
            "timestamp": self.timestamp,
        }

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics including counts and percentages."""
        total_records = len(self.df)
        total_cells = self.df.size
        null_cells = self.df.isna().sum().sum()
        duplicates = total_records - len(self.df.drop_duplicates())

        return {
            "total_records": total_records,
            "total_cells": total_cells,
            "null_cells": null_cells,
            "non_null_cells": total_cells - null_cells,
            "duplicate_records": duplicates,
            "unique_records": total_records - duplicates,
            "completeness_score": round(self.calculate_completeness_score(), 1),
            "duplicate_score": round(self.calculate_duplicate_score(), 1),
            "formatting_score": round(self.calculate_formatting_score(), 1),
            "overall_score": self.calculate_overall_health_score(),
            "timestamp": self.timestamp,
        }
