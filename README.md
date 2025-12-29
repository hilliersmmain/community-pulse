# Community Pulse: Data Analytics Dashboard

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Tests: 70/70](https://img.shields.io/badge/Tests-70%2F70%20passing-brightgreen)](./tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://community-pulse.streamlit.app/)

**Production-ready data analytics dashboard** that transforms messy CSV data into clean, actionable insights with automated cleaning pipelines, interactive visualizations, and comprehensive data quality metrics.

## What It Does

- **Automated Data Cleaning**: Multi-step pipeline handling name standardization, email validation, deduplication, and date formatting
- **Interactive Analytics**: Real-time Plotly visualizations for trend analysis and distribution insights
- **Data Quality Scoring**: Health metrics tracking completeness, uniqueness, and formatting (0-100% scale)
- **Full Test Coverage**: 70 unit tests ensuring reliability and maintainability

## Screenshots

<table>
  <tr>
    <td><img src="./docs/screenshots/dashboard-overview.png" width="400"/><br/><sub>Dashboard with real-time KPIs</sub></td>
    <td><img src="./docs/screenshots/data-cleaning-pipeline.png" width="400"/><br/><sub>Automated cleaning pipeline</sub></td>
  </tr>
  <tr>
    <td><img src="./docs/screenshots/before-after-comparison.png" width="400"/><br/><sub>Before/after comparison</sub></td>
    <td><img src="./docs/screenshots/analytics-trends.png" width="400"/><br/><sub>Interactive analytics</sub></td>
  </tr>
</table>

## Quick Start

```bash
# Clone and navigate
git clone https://github.com/hilliersmmain/community_pulse.git
cd community_pulse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open your browser to `http://localhost:8501`

**Try the [Live Demo](https://community-pulse.streamlit.app/)** — No installation required!

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **Frontend** | Streamlit 1.52+ | Interactive web UI |
| **Data Processing** | Pandas 2.2+ | DataFrame manipulation |
| **Visualization** | Plotly 6.5+ | Interactive charts |
| **Testing** | pytest 9.0+ | 70 unit tests |
| **Data Generation** | Faker, NumPy | Synthetic test data |

## Key Skills Demonstrated

**Python & Data Engineering**
- Clean, modular architecture with reusable components
- Multi-step data transformation pipelines
- Data validation, deduplication, and standardization
- Error handling and logging throughout

**Data Analysis & Visualization**
- Interactive Plotly charts with statistical overlays
- Health scoring algorithms (completeness, uniqueness, formatting)
- Before/after analysis and impact measurement
- DataFrame operations: filtering, grouping, aggregation

**Software Development Practices**
- 70 comprehensive unit tests (100% passing)
- Type hints and docstrings for maintainability
- CI/CD ready with deployment to Streamlit Cloud
- Professional documentation and contribution guidelines

## Project Structure

```
community_pulse/
├── app.py                    # Main Streamlit application
├── utils/                    # Core modules
│   ├── data_generator.py     # Synthetic data with configurable messiness
│   ├── cleaner.py            # Data cleaning pipeline
│   ├── visualizer.py         # Plotly chart creation
│   ├── health_metrics.py     # Data quality scoring
│   └── ui_helpers.py         # UI components
├── tests/                    # 70 unit tests
└── docs/                     # Documentation and screenshots
```

## Testing

```bash
pytest                        # Run all 70 tests
pytest --cov=utils           # Generate coverage report
python verify_setup.py       # Verify installation
```

## Contributing & Documentation

- [CONTRIBUTING.md](./CONTRIBUTING.md) — Contribution guidelines
- [docs/](./docs/) — Detailed technical documentation

## License

MIT License - see [LICENSE](./LICENSE)

---

**Author:** [Samuel M. Hillier](https://github.com/hilliersmmain) | **Live Demo:** [community-pulse.streamlit.app](https://community-pulse.streamlit.app/)
