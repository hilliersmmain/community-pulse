# Community Pulse: Data Analytics Dashboard

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Tests: 70/70](https://img.shields.io/badge/Tests-70%2F70%20passing-brightgreen)](./tests)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://community-pulse.streamlit.app/)

**Community Pulse** is a production-grade data analytics platform that transforms raw, unstructured community data into actionable business intelligence. By automating the entire data engineering lifecycle—from ingestion and cleaning to validation and visualization—it delivers real-time insights into community engagement, growth trends, and member behavior patterns.

### 🧬 Why I Built This
As a former biology student used to dealing with messy organic data, I realized that human community data—with its duplicates, missing fields, and chaotic growth patterns—required the same rigorous treatment as biological datasets. I built **Community Pulse** to prove that a robust, automated data engineering pipeline can be just as elegant as the visualizations it powers. It’s not just a dashboard; it’s an attempt to bring scientific order to social chaos.

---

## 🚀 [**Try the Live Demo →**](https://community-pulse.streamlit.app/)
*No installation required — explore the full dashboard instantly*

---

## 📸 Dashboard Preview
| Dashboard Overview | Data Cleaning Pipeline |
|:--:|:--:|
| ![Dashboard Overview](docs/screenshots/dashboard-overview.png) | ![Data Cleaning](docs/screenshots/data-cleaning-pipeline.png) |

| Before/After Comparison | Data Explorer |
|:--:|:--:|
| ![Comparison](docs/screenshots/before-after-comparison.png) | ![Explorer](docs/screenshots/data-explorer.png) |

---

## 🔑 Key Features
### 1. Automated Data Engineering Pipeline
- **Robust ETL Process:** Ingests raw CSV data, handles missing values, standardizes date formats, and deduplicates records automatically
- **Intelligent Validation:** Enforces strict data quality schemas with configurable rules
- **High Performance:** Optimized for processing datasets with 10,000+ records in seconds

### 2. Interactive Real-Time Analytics Dashboard
- **Live KPI Tracking:** Monitors *Total Messages*, *Active Users*, *Engagement Rates*, and *Growth Velocity* in real-time
- **Dynamic Visualizations:** Plotly-powered interactive charts with drill-down capabilities, date range filtering, and category segmentation
- **Trend Analysis & Forecasting:** Identifies growth patterns, peak activity periods, and anomalies to drive community strategy

### 3. Comprehensive Data Quality Monitoring
- **Automated Health Scoring:** Generates composite "Data Quality Score" based on completeness (40%), uniqueness (30%), and formatting consistency (30%)
- **Before/After Visualization:** Demonstrates pipeline impact with clear metrics improvement tracking

---

## 📊 Impact & Results
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Records Processed** | 500 raw | 450 clean | -10% duplicates removed |
| **Data Quality Score** | 72% | 98% | **+36% relative improvement** |
| **Missing Values** | 23 | 0 | ✅ 100% resolved |
| **Duplicate Records** | 50 (10%) | 0 | ✅ Eliminated |
| **Manual Processing Time** | 2+ hours | 0 | ✅ Fully automated |

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

# Launch the dashboard
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## 📖 Usage Workflow
1. **Generate Data** — Create synthetic community data with configurable messiness levels (100-1000 records)
2. **Configure Cleaning** — Select cleaning algorithms via sidebar toggles or use optimized defaults
3. **Execute Pipeline** — Run automated cleaning with real-time progress logging
4. **Analyze Results** — Explore interactive dashboard with filters, drill-downs, and exports
5. **Export Insights** — Download cleaned data (CSV/JSON) or charts (PNG) for stakeholder presentations

---

## 🛠️ Technology Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit 1.52+ | Interactive web UI with reactive components |
| **Data Processing** | Pandas 2.2+, NumPy | High-performance DataFrame operations |
| **Visualization** | Plotly 6.5+ | Interactive, publication-quality charts |
| **Testing** | pytest 9.0+ | 70 unit tests with 90% code coverage |
| **Data Generation** | Faker | Realistic synthetic data with controlled quality issues |
| **CI/CD** | GitHub Actions | Automated testing, linting, and deployment |

---

## 📁 Project Architecture
```
community-pulse/
├── app.py                    # Main Streamlit application (entry point)
├── utils/                    # Core processing modules
│   ├── data_generator.py     # Synthetic data generation with configurable noise
│   ├── cleaner.py            # Multi-step cleaning pipeline with logging
│   ├── visualizer.py         # Plotly chart components and themes
│   ├── health_metrics.py     # Quality scoring algorithms
│   └── ui_helpers.py         # Reusable UI components
├── tests/                    # 70 comprehensive unit tests
├── docs/                     # Technical documentation
│   ├── API.md                # Module API reference
│   ├── ARCHITECTURAL_OVERVIEW.md
│   └── screenshots/          # Dashboard screenshots
└── .github/workflows/        # CI/CD automation
```

---

## 🧪 Testing & Quality
```bash
pytest                    # Run all 70 tests
pytest --cov=utils        # Generate coverage report
python verify_setup.py    # Verify installation
```

**Quality Metrics:**
- ✅ 70/70 tests passing
- ✅ 90% code coverage
- ✅ Type hints throughout
- ✅ Comprehensive docstrings

---

## 🚀 Deployment
**Streamlit Cloud (Recommended):**
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Deploy with one click

**Live Production Instance:** [community-pulse.streamlit.app](https://community-pulse.streamlit.app/)

**Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

---

## 🎯 Skills & Competencies Demonstrated
**Data Engineering & Analytics**
- End-to-end ETL pipeline design and implementation
- Data quality assessment and automated remediation
- Statistical analysis and KPI definition
- Real-time data processing and visualization

**Software Engineering**
- Modular, maintainable Python architecture
- Comprehensive test coverage (70 tests, 90% coverage)
- CI/CD pipeline with GitHub Actions
- Production deployment of Streamlit Cloud

**Technical Communication**
- Clear documentation and code commenting
- Interactive visualizations for non-technical stakeholders
- API design and developer experience optimization

---

## 👤 About the Developer
I'm **Sam Hillier**, an undergraduate researcher making the transition from cellular biology to artificial intelligence and data science.

- 🎓 **Current:** B.S. Data Science, UNC Charlotte (Transitioning to B.S. Artificial Intelligence, Fall 2026)
- 🧠 **Minor:** Cognitive Science
- 🔬 **History:** I started my university career at **Appalachian State University** (2024-2025), studying Cellular/Molecular Biology. It was there, while modeling biological systems, that I realized I wanted to build the computational tools that analyze the data, not just collect it. This drove my transfer to UNCC to pursue Data Science full-time.
- 📚 **Spring 2026 Coursework:** Human-Centered Computing (ITIS 3130), Computer Science II (ITSC 1213), Mathematics for Computer Science (MATH 2112)

*I'm especially interested in AI applications in neuroscience and human-computer interaction—this project showcases how I apply computational thinking to messy, real-world data problems.*

---

## 📄 License
MIT License — See [LICENSE](./LICENSE) for details.
