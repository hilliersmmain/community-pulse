# Community Pulse: Data Analytics Dashboard

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Tests: 70/70](https://img.shields.io/badge/Tests-70%2F70%20passing-brightgreen)](./tests)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://community-pulse.streamlit.app/)

**Community Pulse** is a production-grade data analytics platform designed to transform raw, unstructured community data into actionable business intelligence. By automating the data engineering lifecycle—from ingestion and cleaning to validation and visualization—it provides real-time insights into community engagement and growth trends.

**[🚀 Try the Live Demo](https://community-pulse.streamlit.app/)** — No installation required

---

## 🔑 Key Features

### 1. Automated Data Engineering Pipeline
- **Robust ETL Process:** Ingests raw CSV data, handles missing values, standardizes date formats, and deduplicates records automatically
- **Validation Layer:** Enforces strict data quality schemas, ensuring only clean, reliable data reaches the dashboard
- **Performance:** Optimized modular design allows for rapid processing of large datasets

### 2. Interactive Analytics Dashboard
- **Real-Time KPIs:** Tracks critical metrics like *Total Messages*, *Active Users*, and *Engagement Rates* instantly
- **Dynamic Visualizations:** Plotly-powered interactive charts allow users to drill down into specific timeframes and categories
- **Trend Analysis:** Visualizes growth patterns and peak activity times to inform community management strategies

### 3. Comprehensive Data Quality Monitoring
- **Health Scoring:** Generates a "Data Quality Score" based on completeness, uniqueness, and consistency
- **Before/After Comparison:** Visualizes the impact of the cleaning pipeline, demonstrating the value of data standardization

---

## 📊 Example Results

| Metric | Before Cleaning | After Cleaning | Improvement |
|--------|-----------------|----------------|-------------|
| Records | 500 | 450 | -10% (duplicates removed) |
| Duplicates | 50 (10%) | 0 | ✓ Eliminated |
| Missing Values | 23 | 0 | ✓ Resolved |
| Health Score | 72% | 98% | **+26%** |

---

## 💻 Quick Start

**Prerequisites:** Python 3.9+

```bash
# Clone and install
git clone https://github.com/hilliersmmain/community-pulse.git
cd community-pulse
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## 📖 Usage Guide

**Workflow:**

1. **Generate Data** — Adjust records (100-1000) and messiness level, click "Generate New Data"
2. **Configure Cleaning** — Toggle cleaning steps in sidebar or use defaults
3. **Run Cleaning** — Navigate to "Data Cleaning Ops" tab, click "Run Cleaning Algorithms"
4. **Analyze Results** — View analytics dashboard, filter by roles, explore charts
5. **Export** — Download CSV/JSON or export charts as PNG

---

## 📁 Project Structure

```
community-pulse/
├── app.py                    # Main Streamlit application
├── utils/                    # Core modules
│   ├── data_generator.py     # Synthetic data generation
│   ├── cleaner.py            # Data cleaning pipeline
│   ├── visualizer.py         # Plotly chart components
│   ├── health_metrics.py     # Quality scoring algorithms
│   └── ui_helpers.py         # UI components
├── tests/                    # 70 comprehensive unit tests
└── docs/                     # Documentation
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit 1.52+ | Interactive web UI |
| **Data Processing** | Pandas 2.2+ | DataFrame manipulation |
| **Visualization** | Plotly 6.5+ | Interactive charts |
| **Testing** | pytest 9.0+ | 70 unit tests (90% coverage) |
| **Data Generation** | Faker, NumPy | Synthetic data creation |

---

## 🧪 Testing

```bash
pytest                    # Run all 70 tests
pytest --cov=utils        # Generate coverage report
python verify_setup.py    # Verify installation
```

**Status:** 70/70 tests passing ✓ | 90% coverage

---

## 🚀 Deployment

**Streamlit Cloud (Recommended):**
1. Push to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Deploy with one click

**Live Demo:** [community-pulse.streamlit.app](https://community-pulse.streamlit.app/)

**Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

---

## 🎯 Skills Demonstrated

**Python & Data Engineering**
- Modular architecture with reusable components
- Data transformation pipelines and validation
- Error handling and logging

**Data Analysis & Visualization**
- Interactive Plotly charts with statistical overlays
- Health scoring algorithms
- DataFrame operations (filtering, grouping, aggregation)

**Software Development**
- 70 comprehensive unit tests with 90% coverage
- Type hints and documentation
- CI/CD deployment to Streamlit Cloud

---

## 📄 License

MIT License — See [LICENSE](./LICENSE) for details.

---

*Developed by **Sam Hillier** — Pursuing B.S. in Artificial Intelligence (Fall 2026) | UNC Charlotte | Minor: Cognitive Science*
