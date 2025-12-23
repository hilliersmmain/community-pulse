# 📊 Community Pulse: Intelligent Data Dashboard

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Tests: 66/66](https://img.shields.io/badge/Tests-66%2F66%20passing-brightgreen)](./tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**Transform your data journey:** Convert messy, unstructured member records into crystal-clear business intelligence in minutes with intelligent data engineering and automated cleaning pipelines.

---

## 🎯 Overview

Community Pulse is a **production-ready Streamlit dashboard** that demonstrates end-to-end data engineering excellence:

- **Data Generation:** Simulate realistic data quality scenarios (CRM cleanliness to legacy system chaos)
- **Intelligent Cleaning Pipeline:** Configurable, auditable data transformation with execution logs
- **Interactive Analytics:** Real-time visualizations with before/after comparison views
- **Data Quality Metrics:** Comprehensive health scoring (completeness, uniqueness, formatting)
- **Export Ready:** CSV, JSON export with versioning and timestamps

**Who it's for:**
- Data engineers building data pipelines
- Analysts who need data quality visibility
- Data teams validating cleaning workflows
- Portfolio projects showcasing full-stack data work

---

## ✨ Key Features

### 1. **Realistic Data Generation**
- Generate 100–1000 member records with configurable messiness
- **Low:** 3% duplicates, 2% errors (well-maintained CRM)
- **Medium:** 10% duplicates, 5% errors (typical export)
- **High:** 20% duplicates, 15% errors (legacy system)

### 2. **Automated Data Cleaning Pipeline**
```python
Configurable steps:
✓ Standardize Names (john doe → John Doe)
✓ Fix Email Formats (user at domain.com → user@domain.com)
✓ Remove Duplicates (email + name matching)
✓ Clean Dates (normalize to YYYY-MM-DD)
✓ Handle Missing Values (fill attendance with 0)
```

### 3. **Data Health Scoring**
Real-time metrics on a 0–100% scale:
- **Completeness Score:** % of non-null cells
- **Duplicate Score:** % of unique records
- **Formatting Score:** % of valid emails, dates, names
- **Overall Health:** Weighted composite score

### 4. **Interactive Analytics Dashboard**
- **Membership Growth:** Time-series trend with linear regression
- **Event Attendance:** Distribution histogram with mean/median annotations
- **Role Demographics:** Pie chart with counts and percentages
- **Before/After Views:** Side-by-side and toggle comparison

### 5. **Before/After Comparison**
- Side-by-side visualization of raw vs. cleaned data
- Impact metrics: records removed, duplicates eliminated, health improvement
- Interactive toggle to explore both states

### 6. **Export & Data Discovery**
- Download raw or cleaned data as CSV/JSON
- Timestamped filenames for version control
- Chart export buttons (PNG at 2x resolution)
- Raw data inspector with health metrics

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.9 or higher
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/hilliersmmain/community_pulse.git
   cd community_pulse
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation (recommended)**
   ```bash
   python scripts/verify_setup.py
   ```
   This script checks that all dependencies are installed correctly.

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

6. **Open in your browser**
   ```
   http://localhost:8501
   ```

---

## 📖 Usage Guide

### Workflow

**Step 1: Generate Sample Data**
1. In the left sidebar, adjust "Number of Records" (100–1000)
2. Select "Messiness Level" (low, medium, or high)
3. Click **"🔄 Generate New Data"**

**Step 2: Configure Cleaning Pipeline**
1. Click **"Configure Cleaning Steps"** in the sidebar
2. Toggle which cleaning operations to apply
3. Or use defaults (all steps enabled)

**Step 3: Run Cleaning**
1. Navigate to **"🧹 Data Cleaning Ops"** tab
2. Click **"🚀 Run Cleaning Algorithms"**
3. Monitor execution log and cleaning summary

**Step 4: Analyze Results**
1. Go to **"📈 Analytics Dashboard"** tab
2. Filter by member roles to focus analysis
3. View interactive charts with detailed tooltips
4. Compare raw vs. cleaned data side-by-side

**Step 5: Export**
1. Download CSV or JSON from sidebar
2. Export charts as high-res PNG (2x scale)
3. Share reports with stakeholders

### Demo Visualizations

Generate static PNG exports of all charts:
```bash
python scripts/demo_charts.py
```
This creates high-quality visualizations in the `demo_outputs/` directory.

---

## 📁 Project Structure

```
community_pulse/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Dependencies
├── README.md                       # This file
├── LICENSE                         # MIT License
│
├── scripts/                        # Utility scripts
│   ├── demo_charts.py              # Generate demo PNG visualizations
│   └── verify_setup.py             # Setup verification script
│
├── artifacts/                      # Previous implementation reports & summaries
│
├── utils/
│   ├── __init__.py
│   ├── data_generator.py          # Synthetic data generation with configurable messiness
│   ├── cleaner.py                 # Data cleaning pipeline with step-by-step logging
│   ├── visualizer.py              # Plotly chart creation (trend, histogram, pie)
│   ├── health_metrics.py          # Data quality scoring algorithm
│   └── ui_helpers.py              # UI components (modals, messages, tooltips)
│
├── tests/
│   ├── test_cleaner.py            # 7 tests for cleaning pipeline
│   ├── test_demo_charts.py        # 7 tests for demo chart generation
│   ├── test_health_metrics.py     # 19 tests for health scoring
│   ├── test_ui_helpers.py         # 15 tests for UI components
│   └── test_visualizer.py         # 18 tests for chart rendering
│
├── docs/
    ├── CONTRIBUTING.md            # Contribution guidelines
    ├── DOCUMENTATION.md           # Detailed technical docs
    ├── KPI_DEFINITIONS.md         # KPI definitions
    └── SOP_DATA_CLEANING.md       # Standard Operating Procedure for cleaning
```

---

## 🧪 Testing

Full test coverage with pytest (66 tests):

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_cleaner.py -v

# Verify setup
python scripts/verify_setup.py
```

**Test Results:** ✅ **66/66 tests passing**

---

## 🛠 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **Frontend** | Streamlit 1.28+ | Interactive web UI with real-time updates |
| **Data Processing** | Pandas 2.0+ | DataFrame manipulation, cleaning operations |
| **Visualization** | Plotly 5.0+ | Interactive charts with export capabilities |
| **Data Generation** | NumPy, Faker | Realistic synthetic data with configurable quality |
| **Testing** | pytest 7.0+ | Unit tests with 45 test cases |
| **Code Quality** | Python 3.9+ | Type hints, docstrings, clean code standards |

---

## 💡 How It Works

### Data Generation Process

```python
generate_messy_data(num_records=500, messiness_level='medium')
```

Creates realistic CSV with intentional quality issues:
- **Names:** Missing values, inconsistent capitalization
- **Emails:** Format errors ("user at domain.com"), typos
- **Dates:** Mixed formats, invalid values
- **Duplicates:** Exact and fuzzy matches
- **Attendance:** Missing values, outliers

### Data Cleaning Pipeline

```python
cleaner = DataCleaner(raw_df)
clean_df = cleaner.clean_all(steps=[
    'standardize_names',
    'fix_emails',
    'remove_duplicates',
    'clean_dates',
    'handle_missing_values'
])
```

Each step is **logged** for auditability:
```
>> [01:23:45] Standardize Names: John doe → John Doe (487 records)
>> [01:23:46] Fix Emails: Removed 12 invalid emails
>> [01:23:47] Remove Duplicates: Removed 45 duplicate records
>> [01:23:48] Clean Dates: Standardized 342 dates to YYYY-MM-DD
>> [01:23:49] Handle Missing: Filled 23 missing attendance values
```

### Health Scoring Algorithm

```
Overall Score = (40% Completeness) + (30% Uniqueness) + (30% Formatting)

Completeness = (Non-null cells / Total cells) × 100
Uniqueness    = (Unique records / Total records) × 100
Formatting    = (Valid emails + dates + names) / Total cells × 100
```

---

## 📊 Example Results

### Before Cleaning
```
📊 Raw Data Metrics:
  • Total Records: 500
  • Duplicate Records: 50 (10%)
  • Missing Values: 23
  • Data Health Score: 72%
```

### After Cleaning
```
✨ Cleaned Data Metrics:
  • Total Records: 450 (50 duplicates removed)
  • Duplicate Records: 0
  • Missing Values: 0
  • Data Health Score: 98% (+26%)
```

---

## 🚢 Deployment

### Option 1: Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. "New app" → Select this repository
4. Streamlit automatically deploys on every push

**Live Demo:** (Add your deployed URL here)

### Option 2: Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t community-pulse .
docker run -p 8501:8501 community-pulse
```

### Option 3: Traditional Server

```bash
# Install systemd service
sudo cp community-pulse.service /etc/systemd/system/
sudo systemctl enable community-pulse
sudo systemctl start community-pulse

# Use nginx as reverse proxy on port 80
```

---

## 🎓 Learning & Portfolio Value

This project demonstrates:

✅ **Data Engineering**
- Data generation with realistic quality issues
- Multi-step cleaning pipelines
- Comprehensive error handling

✅ **Data Analysis**
- Health scoring algorithms
- Statistical analysis (mean, median, std dev)
- Trend detection (linear regression)

✅ **Frontend & UX**
- Responsive Streamlit design
- Interactive Plotly visualizations
- Real-time metric updates
- Modal dialogs and form validation

✅ **Software Engineering**
- Modular code architecture
- 59 passing unit tests
- Type hints and docstrings
- Comprehensive documentation

✅ **Production Readiness**
- Error handling and recovery
- Session state management
- Configuration flexibility
- Audit logging

---

## 📝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.

**Ideas for enhancement:**
- [ ] Database backend (PostgreSQL/MongoDB)
- [ ] Multi-file upload support
- [ ] Advanced filtering (date range, value ranges)
- [ ] Machine learning anomaly detection
- [ ] Email report generation
- [ ] API layer (FastAPI)

---

## 📄 Documentation

- **[DOCUMENTATION.md](./docs/DOCUMENTATION.md)** — Detailed technical reference
- **[CONTRIBUTING.md](./docs/CONTRIBUTING.md)** — How to contribute
- **[KPI_DEFINITIONS.md](./docs/KPI_DEFINITIONS.md)** — KPI reference

---

## 📜 License

MIT License - see [LICENSE](./LICENSE) for details.

---

## 👤 Author

**Samuel M. Hillier**
- GitHub: [@hilliersmmain](https://github.com/hilliersmmain)
- Portfolio: [Community Pulse GitHub](https://github.com/hilliersmmain/community_pulse)

---

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io) — App framework
- [Plotly](https://plotly.com) — Interactive visualizations
- [Pandas](https://pandas.pydata.org) — Data manipulation
- [Faker](https://github.com/joke2k/faker) — Synthetic data

---

## 📞 Support

- 📖 Check [DOCUMENTATION.md](./docs/DOCUMENTATION.md)
- 🐛 Report issues on [GitHub Issues](https://github.com/hilliersmmain/community_pulse/issues)
- 💡 Discuss ideas in [GitHub Discussions](https://github.com/hilliersmmain/community_pulse/discussions)

---

**⭐ If this project helped you, please consider starring it!**
