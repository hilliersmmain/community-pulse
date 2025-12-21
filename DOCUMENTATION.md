# Project Documentation

## 1. Project Overview

Nonprofit organizations often struggle with "messy" data exported from legacy CRMs—duplicates, inconsistent formatting, and missing information. **Community Pulse** solves this by providing a lightweight, automated pipeline to clean this data and immediately visualize it in an interactive dashboard.

## 2. Architecture

The application follows a simple functional architecture:

```text
[Data Source] -> [DataCleaner Class] -> [Pandas DataFrame] -> [Visualizer Module] -> [Streamlit UI]
```

- **`data_generator.py`**: Uses the `Faker` library to synthesize realistic robust datasets with intentional errors (entropy).
- **`cleaner.py`**: The core logic engine. It encapsulates data cleaning rules into a reusable `DataCleaner` object.
- **`visualizer.py`**: A pure functional module that takes a DataFrame and returns Plotly Figure objects.
- **`app.py`**: Tying it all together in a reactive web interface.

## 3. Key Features Deep Dive

### Data Cleaning Logic (`utils/cleaner.py`)

The pipeline runs in a specific order to maximize efficiency:

1.  **Standardization**: Converts inputs to standard formats (e.g., Title Case for names, lowercase for emails).
2.  **Deduplication**: Identifies duplicates based on normalized email addresses, keeping the primary record.
3.  **Type Coercion**: Forces date columns into proper `datetime` objects, handling errors gracefully.
4.  **Imputation**: Fills missing values (e.g., setting missing attendance to 0) to ensure charts render correctly.

### Visualization (`utils/visualizer.py`)

- **Growth Trend**: A line chart aggregating new members by month.
- **Role Distribution**: A pie chart showing the breakdown of Members vs. Admins.
- **Attendance Histogram**: A frequency distribution of event attendance to identify "Super Users".

## 4. Code Example: Using the Cleaner Standalone

You can use the cleaning logic outside of the web app (e.g., in a Jupyter Notebook):

```python
from utils.cleaner import DataCleaner
import pandas as pd

# Load your raw CSV
df = pd.read_csv('my_messy_export.csv')

# Initialize and Clean
cleaner = DataCleaner(df)
clean_df = cleaner.clean_all()

# View the log of changes
print(cleaner.log)
# Output: ['Standardized Names...', 'Removed 12 duplicates...']

# Save result
clean_df.to_csv('clean_data.csv', index=False)
```

## 5. Deployment Guide

### Deploying to Streamlit Community Cloud

1.  Push this code to a public GitHub repository.
2.  Log in to [share.streamlit.io](https://share.streamlit.io/).
3.  Click "New App".
4.  Select your repository and the `app.py` file.
5.  Click "Deploy".

### Future Enhancements

- **PDF Export**: Generate a downloadable PDF report of the cleaning logs.
- **Email Validation API**: Integrate with an external API (like ZeroBounce) for real validation.
- **Database Sync**: Connect directly to a SQL database instead of CSV files.
