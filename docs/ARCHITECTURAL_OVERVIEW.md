# Project Documentation

## 1. Project Overview

Nonprofit organizations often struggle with "messy" data exported from legacy CRMs—duplicates, inconsistent formatting, and missing information. **Community Pulse** solves this by providing a lightweight, automated pipeline to clean this data and immediately visualize it in an interactive dashboard.

## 2. Architecture

The application follows a simple functional architecture:

```text
[DataGenerator / CSV upload] -> [st.session_state["raw_df"]] -> [DataCleaner] -> [DataHealthMetrics] -> [Visualizer] -> [Streamlit UI]
```

Each browser session keeps its own data in `st.session_state` (raw data under `"raw_df"`, cleaned data under `"clean_df"`); nothing is written to the server's disk, so one visitor never sees another's data.

**`utils/`: the logic**

- **`data_generator.py`**: Uses the `Faker` library to synthesize realistic member data with intentional errors.
- **`upload_validation.py`**: Checks an uploaded CSV (column count from the raw header, required columns, row count) before the app uses it.
- **`cleaner.py`**: The core logic engine. It encapsulates data cleaning rules into a reusable `DataCleaner` object.
- **`duplicates.py`**: The one definition of a duplicate (same Email, ignoring case and surrounding spaces), shared by the cleaner and the health metrics.
- **`date_parsing.py`**: Parses date columns that mix several formats; unreadable dates become NaT.
- **`health_metrics.py`**: Completeness, Duplicate, Formatting and overall Data Health scores (see [KPI_DEFINITIONS.md](KPI_DEFINITIONS.md)).
- **`visualizer.py`**: A pure functional module that takes a DataFrame and returns Plotly Figure objects.
- **`ui_helpers.py`**, **`session_keys.py`**, **`constants.py`**: Shared UI helpers (tutorial, toasts, messages), session-state key names, and the shared tunables (chart colours, record-count and upload limits, cleaning defaults, score weights and thresholds, date formats, email and name patterns).

**`components/`: the UI**

- **`sidebar.py`**: Data source (generate or upload), cleaning-step choices, export, view toggle, help.
- **`kpi_display.py`**: The Key Performance Indicators row.
- **`comparison.py`**: The before/after cleaning comparison tiles.
- **`tab_preparation.py`**, **`tab_analytics.py`**, **`tab_explorer.py`**: The Data Preparation, Analytics and Data Explorer tabs.

**`app.py`**: A thin orchestrator: loads this session's data, sets up state and calls the render functions.

## 3. Key Features Deep Dive

### Data Cleaning Logic (`utils/cleaner.py`)

The pipeline always runs its selected steps in this order:

1.  **Standardize Names**: Title Case for names written entirely in upper or lower case; mixed-case names are kept.
2.  **Fix Email Formats**: Lower-cases emails, turns " at " into "@", and drops rows whose email is still invalid or blank.
3.  **Remove Duplicates**: Removes rows whose email (ignoring case and surrounding spaces) repeats an earlier row, keeping the first. It runs after the email fix, so repaired addresses are matched too.
4.  **Clean Dates**: Parses `Join_Date` into `datetime` values; a date nothing can read is left blank (NaT), never guessed.
5.  **Handle Missing Values**: Sets missing or non-numeric `Event_Attendance` to 0 so the attendance chart renders correctly.

### Visualization (`utils/visualizer.py`)

- **Growth Trend**: A line chart aggregating new members by month.
- **Role Distribution**: A pie chart showing the breakdown of Members, Admins and Guests.
- **Attendance Histogram**: A frequency distribution of event attendance, with mean and median lines.

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
# Output: ['Standardized Names to Title Case.', 'Fixed email formatting. Removed 0 invalid emails.',
#          'Removed 51 duplicate rows.', ...]

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

## 6. Scalability & Implementation Plan

### Phase 1: Current State (Prototype)

**Target Audience**: Single nonprofit organization, data team of 1-3 users  
**Infrastructure**: Local Streamlit app or Streamlit Community Cloud  
**Data Volume**: Uploads up to 50,000 rows, 50 columns and 5 MB; generated samples of 100 to 1,000 records  
**Storage**: In memory, per browser session (`st.session_state`); nothing is saved on the server

**Current Capabilities**:

- Interactive data cleaning with real-time feedback
- Basic analytics dashboard with role filtering
- CSV and JSON export of raw or cleaned data
- Manual data generation for testing

**Limitations**:

- No persistent storage: data lasts only as long as the browser session
- Each visitor works alone on their own data; nothing is shared between sessions
- No authentication or user management
- CSV is the only upload format

---

### Phase 2: Production (Multi-User)

**Target Audience**: Mid-size nonprofit (50-500 active users), data operations team  
**Infrastructure**: Cloud-hosted (AWS/GCP/Azure) with containerization  
**Data Volume**: 50,000-100,000 member records  
**Storage**: PostgreSQL or MySQL database

**Key Enhancements**:

1. **Database Integration**

   - Replace CSV files with PostgreSQL database
   - Implement data persistence across sessions
   - Add database backup and recovery procedures

2. **Authentication & Access Control**

   - User login system with role-based permissions
   - Admin users: Full access to cleaning and settings
   - Regular users: View-only dashboard access
   - Audit logging for all data operations

3. **Automated Workflows**

   - Scheduled cleaning jobs (e.g., daily at 2 AM)
   - Email notifications for cleaning completion
   - Automated CRM data sync via API integrations

4. **Enhanced Analytics**

   - Historical trend tracking (year-over-year comparisons)
   - Predictive analytics using machine learning
   - Custom report builder with export to PDF/Excel

5. **Performance Optimization**
   - Caching for frequently-accessed data
   - Pagination for large datasets
   - Asynchronous processing for cleaning operations

**Estimated Timeline**: 3-4 months  
**Team Requirements**: 1 Backend Developer, 1 Frontend Developer, 1 DevOps Engineer

---

### Phase 3: Enterprise (SaaS Platform)

**Target Audience**: Multiple organizations, enterprise nonprofits, SaaS customers  
**Infrastructure**: Multi-tenant cloud architecture with auto-scaling  
**Data Volume**: 1M+ records across all tenants  
**Storage**: Distributed database (e.g., Amazon RDS with read replicas)

**Key Enhancements**:

1. **Multi-Tenancy Architecture**

   - Separate data isolation for each organization
   - Tenant-specific configurations and branding
   - Organization-level usage quotas and billing

2. **RESTful API Layer**

   - Public API for third-party integrations
   - Webhook support for real-time data sync
   - API rate limiting and authentication (OAuth 2.0)

3. **Advanced CRM Integrations**

   - Pre-built connectors for Salesforce, HubSpot, Blackbaud
   - Two-way sync: read from CRM, write cleaned data back
   - Field mapping customization per organization

4. **Enterprise Features**

   - Advanced data validation rules (custom regex, business logic)
   - Data quality scoring and recommendations
   - Compliance reporting (GDPR, data retention policies)
   - White-label deployment options

5. **Scalability & Reliability**

   - Horizontal scaling with load balancers
   - 99.9% uptime SLA with redundancy
   - Real-time monitoring and alerting (Datadog, New Relic)
   - Disaster recovery with automated backups

6. **Advanced Analytics & AI**
   - Anomaly detection for data quality issues
   - Member churn prediction models
   - Natural language queries for dashboard insights
   - Customizable KPI thresholds per organization

**Estimated Timeline**: 12-18 months  
**Team Requirements**: 3 Backend Developers, 2 Frontend Developers, 2 DevOps Engineers, 1 ML Engineer, 1 Product Manager

---

### Migration Path

Organizations can seamlessly upgrade between phases:

1. **Phase 1 → Phase 2**: Export CSV data, import to production database, configure authentication
2. **Phase 2 → Phase 3**: Tenant migration wizard, API key generation, CRM connector setup

Each phase builds on the previous foundation while maintaining backward compatibility where possible.
