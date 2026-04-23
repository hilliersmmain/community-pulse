"""Constants and configuration values for Community Pulse."""

DATA_PATH = "data/messy_club_data.csv"
DATA_DIR = "data"

DEFAULT_NUM_RECORDS = 500
DEFAULT_MESSINESS = "medium"
MESSINESS_OPTIONS = ["low", "medium", "high"]
MIN_RECORDS = 100
MAX_RECORDS = 1000
RECORDS_STEP = 50

REQUIRED_COLUMNS = ["Name", "Email", "Role", "Join_Date", "Event_Attendance"]
OPTIONAL_COLUMNS = ["Join_Date", "Last_Login", "Event_Attendance", "Role", "Event_Registered", "Registration_Date"]

MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_ROWS = 50000

CLEANING_STEPS_DEFAULT = {
    "standardize_names": True,
    "fix_emails": True,
    "remove_duplicates": True,
    "clean_dates": True,
    "handle_missing_values": True,
}

SCORE_THRESHOLDS = {
    "excellent": 90,
    "good": 70,
}

CUSTOM_CSS = """
<style>
    .main h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #1f77b4;
    }

    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        font-weight: 500;
    }

    div.css-1r6slb0, div.stMetric {
        padding: 1rem;
        border-radius: 8px;
    }

    .element-container div[data-testid="stMarkdownContainer"] > div[data-testid="stMarkdown"] {
        font-size: 0.95rem;
    }

    .js-plotly-plot {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
"""
