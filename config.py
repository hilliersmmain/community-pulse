"""
Configuration file for Community Pulse application.

This module contains all configuration constants and magic numbers used throughout the application.
"""

# Data Generation Configuration
DEFAULT_NUM_RECORDS = 500
DUPLICATE_RATE = 0.1  # 10% of records will be duplicates
INVALID_EMAIL_RATE = 0.05  # 5% of emails will be invalid
MISSING_VALUE_RATE = 0.05  # 5% of values will be missing
MIXED_CASE_NAME_RATE = 0.2  # 20% of names will have mixed case issues
INCONSISTENT_DATE_RATE = 0.45  # 45% of dates will have format issues

# Data Paths
DEFAULT_DATA_DIR = "data"
DEFAULT_DATA_FILE = "messy_club_data.csv"

# Data Cleaning Configuration
FUZZY_MATCH_THRESHOLD = 0.85  # Similarity threshold for fuzzy name matching
EMAIL_REGEX_PATTERN = r"[^@]+@[^@]+\.[^@]+"

# Role Distribution (probabilities must sum to 1.0)
ROLE_PROBABILITIES = {
    "Member": 0.8,
    "Admin": 0.05,
    "Guest": 0.15
}

# Event Choices
EVENT_CHOICES = ["Spring Gala", "Summer Camp", "Fall Fundraiser", "None"]
EVENT_PROBABILITIES = [0.25, 0.25, 0.25, 0.25]

# File Upload Configuration
MAX_UPLOAD_SIZE_MB = 50
ALLOWED_FILE_EXTENSIONS = ['.csv']

# Data Health Score Configuration
# Formula: 100 - (duplicate_rate + missing_rate + invalid_email_rate)
# Each rate is calculated as a percentage

# Predictive Analytics Configuration
PREDICTION_WINDOW_MONTHS = 3  # Use 3-month moving average for predictions

# KPI Targets
TARGET_DUPLICATE_RATE = 5.0  # Maximum acceptable duplicate rate (%)
TARGET_MISSING_RATE = 3.0  # Maximum acceptable missing data rate (%)
TARGET_EMAIL_VALIDITY_RATE = 95.0  # Minimum acceptable email validity rate (%)
TARGET_DATA_HEALTH_SCORE = 90.0  # Minimum acceptable overall data health score

# Phone Number Formats
PHONE_FORMATS = [
    r'\((\d{3})\)\s*(\d{3})-(\d{4})',  # (555) 123-4567
    r'(\d{3})-(\d{3})-(\d{4})',        # 555-123-4567
    r'(\d{10})'                         # 5551234567
]
PHONE_OUTPUT_FORMAT = "({}) {}-{}"  # Standard output format

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Visualization Configuration
CHART_HEIGHT = 400
CHART_WIDTH = 600
COLOR_PALETTE = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
