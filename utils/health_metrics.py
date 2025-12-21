"""
Data Health Metrics Module

This module provides functionality to calculate comprehensive health scores
for datasets, measuring data quality across multiple dimensions including
completeness, duplicates, and formatting consistency.
"""

import pandas as pd
import re
from typing import Dict, Tuple
from datetime import datetime


class DataHealthMetrics:
    """
    Calculate comprehensive health metrics for a dataset.
    
    Measures data quality across three key dimensions:
    1. Completeness: Percentage of non-null values
    2. Duplicates: Percentage of unique records
    3. Formatting: Validity of emails, dates, and other formatted fields
    
    Attributes:
        df (pd.DataFrame): The dataset to analyze
        timestamp (datetime): When the analysis was performed
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the DataHealthMetrics calculator.
        
        Args:
            df (pd.DataFrame): The dataset to analyze
        """
        self.df = df.copy()
        self.timestamp = datetime.now()
    
    def calculate_completeness_score(self) -> float:
        """
        Calculate the completeness score based on non-null values.
        
        Returns:
            float: Completeness score between 0 and 100
        """
        if self.df.empty:
            return 0.0
        
        total_cells = self.df.size
        non_null_cells = total_cells - self.df.isna().sum().sum()
        
        return (non_null_cells / total_cells) * 100
    
    def calculate_duplicate_score(self) -> float:
        """
        Calculate the duplicate score based on unique records.
        
        Returns:
            float: Score between 0 and 100 (100 = no duplicates)
        """
        if len(self.df) == 0:
            return 100.0
        
        # Check for exact duplicates
        unique_rows = len(self.df.drop_duplicates())
        total_rows = len(self.df)
        
        return (unique_rows / total_rows) * 100
    
    def calculate_formatting_score(self) -> float:
        """
        Calculate the formatting score based on field validity.
        
        Checks:
        - Email format validity
        - Date format validity
        - Name format (no excessive special characters)
        
        Returns:
            float: Formatting score between 0 and 100
        """
        scores = []
        
        # Email validation
        if 'Email' in self.df.columns:
            valid_emails = self.df['Email'].apply(self._is_valid_email).sum()
            email_score = (valid_emails / len(self.df)) * 100
            scores.append(email_score)
        
        # Date validation
        if 'Join_Date' in self.df.columns:
            valid_dates = self._count_valid_dates('Join_Date')
            date_score = (valid_dates / len(self.df)) * 100
            scores.append(date_score)
        
        # Name validation (should be title case or reasonable format)
        if 'Name' in self.df.columns:
            valid_names = self.df['Name'].apply(self._is_valid_name).sum()
            name_score = (valid_names / len(self.df)) * 100
            scores.append(name_score)
        
        # Return average of all formatting scores
        return sum(scores) / len(scores) if scores else 100.0
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Check if an email is in a valid format.
        
        Args:
            email: Email string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if pd.isna(email):
            return False
        
        email_str = str(email).strip()
        # Basic email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email_str))
    
    def _is_valid_name(self, name: str) -> bool:
        """
        Check if a name is in a reasonable format.
        
        Args:
            name: Name string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if pd.isna(name):
            return False
        
        name_str = str(name).strip()
        # Check for basic name validity (letters, spaces, hyphens, apostrophes)
        pattern = r'^[a-zA-Z\s\-\'\.]+$'
        return bool(re.match(pattern, name_str)) and len(name_str) > 0
    
    def _count_valid_dates(self, column: str) -> int:
        """
        Count valid dates in a column.
        
        Args:
            column: Name of the date column
            
        Returns:
            int: Number of valid dates
        """
        try:
            # Try to parse dates
            parsed = pd.to_datetime(self.df[column], errors='coerce')
            return parsed.notna().sum()
        except Exception:
            return 0
    
    def calculate_overall_health_score(self) -> float:
        """
        Calculate the overall health score as a weighted average.
        
        Weights:
        - Completeness: 40%
        - Duplicates: 30%
        - Formatting: 30%
        
        Returns:
            float: Overall health score between 0 and 100
        """
        completeness = self.calculate_completeness_score()
        duplicates = self.calculate_duplicate_score()
        formatting = self.calculate_formatting_score()
        
        # Weighted average
        overall = (completeness * 0.4) + (duplicates * 0.3) + (formatting * 0.3)
        
        return round(overall, 1)
    
    def get_all_metrics(self) -> Dict[str, float]:
        """
        Get all health metrics in a single dictionary.
        
        Returns:
            Dict[str, float]: Dictionary containing all health metrics
        """
        return {
            'completeness_score': round(self.calculate_completeness_score(), 1),
            'duplicate_score': round(self.calculate_duplicate_score(), 1),
            'formatting_score': round(self.calculate_formatting_score(), 1),
            'overall_score': self.calculate_overall_health_score(),
            'timestamp': self.timestamp
        }
    
    def get_detailed_metrics(self) -> Dict[str, any]:
        """
        Get detailed metrics including counts and percentages.
        
        Returns:
            Dict: Detailed metrics dictionary
        """
        total_records = len(self.df)
        total_cells = self.df.size
        null_cells = self.df.isna().sum().sum()
        duplicates = total_records - len(self.df.drop_duplicates())
        
        return {
            'total_records': total_records,
            'total_cells': total_cells,
            'null_cells': null_cells,
            'non_null_cells': total_cells - null_cells,
            'duplicate_records': duplicates,
            'unique_records': total_records - duplicates,
            'completeness_score': round(self.calculate_completeness_score(), 1),
            'duplicate_score': round(self.calculate_duplicate_score(), 1),
            'formatting_score': round(self.calculate_formatting_score(), 1),
            'overall_score': self.calculate_overall_health_score(),
            'timestamp': self.timestamp
        }
