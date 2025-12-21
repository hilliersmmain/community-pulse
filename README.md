# Community Pulse: Intelligent Data Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-green)

**Transforming messy, raw member data into actionable insights.**

Community Pulse is a demonstration of pure Python data engineering and dashboarding. It takes simulated "dirty" CRM data—riddled with duplicates, typos, and missing values—and passes it through an automated cleaning pipeline to power a live interactive dashboard.

## 🎯 What It Does

1.  **Generates Entropy:** Creates a highly realistic "messy" dataset (simulating a nonprofit's exported CSV).
2.  **Cleans Automatically:** Uses a custom `DataCleaner` class to fix emails, merge duplicates, and standardize dates.
3.  **Visualizes Impacts:** Shows immediate "Before vs. After" metrics and interactive Plotly charts of the cleaned data.

## ✨ Key Features

- **Automated Data Cleaning Pipeline:** Handles duplicates, fuzzy string matching (names), and type coercion.
- **Interactive Analytics:** Real-time Plotly charts for attendance trends, role distribution, and engagement.
- **AI-Lite Prediction:** Simple moving average logic to project future attendance.
- **Professional UI:** Built with Streamlit for a clean, responsive user experience.

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly Express
- **Data Generation:** Faker

## 🚀 Getting Started

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/community_pulse.git
    cd community_pulse
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

Run the application locally:

```bash
streamlit run app.py
```

_(Or use the included `run_community_pulse.bat` on Windows)_

## 📂 Project Structure

```text
community_pulse/
├── app.py              # Main Application Entry Point
├── requirements.txt    # Project Dependencies
├── data/               # Local data storage (ignored by git)
└── utils/
    ├── data_generator.py # Creates the "messy" data
    ├── cleaner.py        # Core cleaning logic class
    └── visualizer.py     # Plotly charting functions
```

## 🎓 Portfolio Context

This project was designed to demonstrate specific competencies for Data Science roles:

- **Data Cleaning:** Handling real-world dirty data (Target: Autism Strong Foundation).
- **Dashboarding:** Building KPI visualizations (Target: Transfer Center).
- **App Development:** Creating functional software tools (Target: Pivot Point Analytics).

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
