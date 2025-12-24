# Community Pulse: Data Analytics Dashboard

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Tests: 70/70](https://img.shields.io/badge/Tests-70%2F70%20passing-brightgreen)](./tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://community-pulse.streamlit.app/)

**End-to-end data analytics project:** Transform messy CSV data into clean, actionable insights with automated data cleaning pipelines, interactive visualizations, and comprehensive data quality metrics.

---

## Overview

Community Pulse is a **production-ready data analytics dashboard** built with Python and Streamlit that demonstrates professional-grade data engineering and visualization skills:

- **Automated Data Cleaning:** Multi-step pipeline with standardization, deduplication, and validation
- **Interactive Analytics:** Real-time visualizations with Plotly for trend analysis and distribution insights
- **Data Quality Metrics:** Comprehensive health scoring (completeness, uniqueness, formatting)
- **Full Test Coverage:** 70 unit tests ensuring code reliability and maintainability
- **Export Capabilities:** CSV/JSON downloads with timestamps for reporting

**Perfect for:**
- Data science/analytics students building a portfolio
- Analysts demonstrating end-to-end data pipeline skills
- Recruiters evaluating Python, Pandas, and data visualization expertise
- Teams seeking data quality automation templates

---

## Key Features

### 1. **Dashboard Overview with Real-Time KPIs**
Monitor data quality metrics with comprehensive health scores displayed on interactive cards.

![Dashboard Overview](./docs/screenshots/dashboard-overview.png)
*Main dashboard showing KPI cards with data health metrics, including total records, duplicates, missing values, and overall health score*

### 2. **Automated Data Cleaning Pipeline**
Execute intelligent data cleaning operations with configurable steps and real-time execution logs.

![Data Cleaning Pipeline](./docs/screenshots/data-cleaning-pipeline.png)
*Data Cleaning Pipeline interface with configurable cleaning steps and the "Run Cleaning Algorithms" button*

**Configurable cleaning steps:**
- Standardize Names (john doe → John Doe)
- Fix Email Formats (user at domain.com → user@domain.com)
- Remove Duplicates (email + name matching)
- Clean Dates (normalize to YYYY-MM-DD)
- Handle Missing Values (fill attendance with 0)

### 3. **Before/After Cleaning Comparison**
Visualize the impact of data cleaning with side-by-side metrics showing improvements in data quality.

![Before/After Comparison](./docs/screenshots/before-after-comparison.png)
*Before vs. After comparison showing improvements in records, duplicates, missing values, and health score*

### 4. **Interactive Analytics Dashboard**
Explore data with interactive visualizations including membership growth trends, attendance distributions, and role demographics.

![Analytics - Membership Trends](./docs/screenshots/analytics-trends.png)
*Membership growth over time chart with trend line analysis*

![Analytics - Attendance Distribution](./docs/screenshots/analytics-distribution.png)
*Event attendance distribution histogram with statistical annotations (mean, median, standard deviation)*

### 5. **Data Explorer & Inspector**
Dive deep into data with health metrics overview and detailed inspection capabilities.

![Data Explorer](./docs/screenshots/data-explorer.png)
*Data Explorer tab showing data health overview with completeness, uniqueness, formatting, and overall health metrics*

### 6. **Additional Capabilities**
- **Realistic Data Generation:** 100–1000 records with configurable messiness (low/medium/high)
- **Data Health Scoring:** Real-time metrics on 0–100% scale
- **Export & Discovery:** Download CSV/JSON with timestamps, chart exports at 2x resolution
- **Before/After Views:** Side-by-side and toggle comparison modes

---

## Quick Start

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
   python verify_setup.py
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

## Usage Guide

### Workflow

**Step 1: Generate Sample Data**
1. In the left sidebar, adjust "Number of Records" (100–1000)
2. Select "Messiness Level" (low, medium, or high)
3. Click **"Generate New Data"**

**Step 2: Configure Cleaning Pipeline**
1. Click **"Configure Cleaning Steps"** in the sidebar
2. Toggle which cleaning operations to apply
3. Or use defaults (all steps enabled)

**Step 3: Run Cleaning**
1. Navigate to **"Data Cleaning Ops"** tab
2. Click **"Run Cleaning Algorithms"**
3. Monitor execution log and cleaning summary

**Step 4: Analyze Results**
1. Go to **"Analytics Dashboard"** tab
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
python community_pulse/demo_charts.py
```
This creates high-quality visualizations in the `demo_outputs/` directory.

---

## Project Structure

```
community_pulse/
├── app.py                          # Main Streamlit application
├── verify_setup.py                 # Setup verification script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── LICENSE                         # MIT License
├── CONTRIBUTING.md                 # Contribution guidelines
├── FINAL_ASSESSMENT.md             # Project evaluation
│
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
│
├── .devcontainer/
│   └── devcontainer.json           # VS Code dev container config
│
├── .github/
│   └── workflows/                  # GitHub Actions workflows
│
├── utils/
│   ├── __init__.py
│   ├── data_generator.py           # Synthetic data generation with configurable messiness
│   ├── cleaner.py                  # Data cleaning pipeline with step-by-step logging
│   ├── visualizer.py               # Plotly chart creation (trend, histogram, pie)
│   ├── health_metrics.py           # Data quality scoring algorithm
│   └── ui_helpers.py               # UI components (modals, messages, tooltips)
│
├── community_pulse/
│   ├── __init__.py
│   └── demo_charts.py              # Generate demo PNG visualizations
│
├── tests/
│   ├── __init__.py
│   ├── test_cleaner.py             # Tests for cleaning pipeline
│   ├── test_demo_charts.py         # Tests for demo chart generation
│   ├── test_emoji_removal.py       # Tests for emoji handling
│   ├── test_health_metrics.py      # Tests for health scoring
│   ├── test_ui_helpers.py          # Tests for UI components
│   └── test_visualizer.py          # Tests for chart rendering
│
├── docs/
│   ├── screenshots/                # Application screenshots (6 images)
│   ├── ARCHITECTURAL_OVERVIEW.md   # Technical architecture details
│   ├── KPI_DEFINITIONS.md          # Key performance indicators
│   └── SOP_DATA_CLEANING.md        # Standard operating procedures
│
└── artifacts/
    └── *.md                        # Project documentation archives
```

---

## Testing

Full test coverage with pytest (70 tests):

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_cleaner.py -v

# Verify setup
python verify_setup.py
```

**Test Results:** **70/70 tests passing**

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **Frontend** | Streamlit 1.52+ | Interactive web UI with real-time updates |
| **Data Processing** | Pandas 2.2+ | DataFrame manipulation, cleaning operations |
| **Visualization** | Plotly 6.5+ | Interactive charts with export capabilities |
| **Data Generation** | NumPy, Faker | Realistic synthetic data with configurable quality |
| **Testing** | pytest 9.0+ | Unit tests with 70 test cases |
| **Code Quality** | Python 3.9+ | Type hints, docstrings, clean code standards |

---

## How It Works

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

## Example Results

### Before Cleaning
```
Raw Data Metrics:
  • Total Records: 500
  • Duplicate Records: 50 (10%)
  • Missing Values: 23
  • Data Health Score: 72%
```

### After Cleaning
```
Cleaned Data Metrics:
  • Total Records: 450 (50 duplicates removed)
  • Duplicate Records: 0
  • Missing Values: 0
  • Data Health Score: 98% (+26%)
```

---

## Deployment

### Option 1: Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. "New app" → Select this repository
4. Streamlit automatically deploys on every push

**Live Demo:** [https://community-pulse.streamlit.app/](https://community-pulse.streamlit.app/)

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

## How This Demonstrates My Skills

This project showcases key competencies for **data science and analytics roles**:

### **Python Programming**
- Clean, modular code architecture with reusable utility modules
- Type hints and comprehensive docstrings for maintainability
- Error handling and input validation throughout the codebase
- Professional code organization following Python best practices

### **Data Manipulation & Cleaning (Pandas)**
- Multi-step data transformation pipelines
- Handling missing values, duplicates, and data quality issues
- DataFrame operations: filtering, grouping, aggregation
- Data validation and standardization techniques

### **Data Visualization (Plotly)**
- Interactive charts with hover tooltips and drill-down capabilities
- Multiple visualization types: line charts, histograms, pie charts
- Statistical overlays (mean, median, trend lines)
- Export-ready visualizations at high resolution

### **Web Application Development (Streamlit)**
- Interactive dashboard with session state management
- Responsive UI components and form validation
- Real-time data updates and user feedback
- Configuration panels and export functionality

### **Software Testing & Quality**
- 70 comprehensive unit tests covering all core functionality
- Test-driven development approach ensuring code reliability
- Edge case handling and validation testing
- Continuous integration-ready test suite

### **Data Analytics Skills**
- Data quality assessment and health scoring algorithms
- Before/after analysis and impact measurement
- Statistical analysis (mean, median, standard deviation)
- Trend detection using linear regression

### **Professional Development Practices**
- Version control with Git and GitHub
- Clear documentation and contribution guidelines
- Deployment to cloud platforms (Streamlit Cloud)
- Production-ready code with error handling and logging

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Ideas for enhancement:**
- [ ] Database backend (PostgreSQL/MongoDB)
- [ ] Multi-file upload support
- [ ] Advanced filtering (date range, value ranges)
- [ ] Machine learning anomaly detection
- [ ] Email report generation
- [ ] API layer (FastAPI)

---

## Documentation

- **[ARCHITECTURAL_OVERVIEW.md](./docs/ARCHITECTURAL_OVERVIEW.md)** — Technical architecture details
- **[KPI_DEFINITIONS.md](./docs/KPI_DEFINITIONS.md)** — Key performance indicators
- **[SOP_DATA_CLEANING.md](./docs/SOP_DATA_CLEANING.md)** — Standard operating procedures
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** — How to contribute

---

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

## Author

**Samuel M. Hillier**
- GitHub: [@hilliersmmain](https://github.com/hilliersmmain)
- Portfolio: [Community Pulse GitHub](https://github.com/hilliersmmain/community_pulse)

---

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io) — App framework
- [Plotly](https://plotly.com) — Interactive visualizations
- [Pandas](https://pandas.pydata.org) — Data manipulation
- [Faker](https://github.com/joke2k/faker) — Synthetic data

---

## Support

- Check the [documentation files](./docs/) for detailed guides
- Report issues on [GitHub Issues](https://github.com/hilliersmmain/community_pulse/issues)
- Discuss ideas in [GitHub Discussions](https://github.com/hilliersmmain/community_pulse/discussions)

---

**If this project helped you, please consider starring it!**
