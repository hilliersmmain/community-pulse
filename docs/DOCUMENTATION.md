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

## 6. Scalability & Implementation Plan

### Phase 1: Current State (Prototype)

**Target Audience**: Single nonprofit organization, data team of 1-3 users  
**Infrastructure**: Local Streamlit app or Streamlit Community Cloud  
**Data Volume**: Up to 10,000 member records  
**Storage**: CSV files stored locally or in the app's data directory

**Current Capabilities**:

- Interactive data cleaning with real-time feedback
- Basic analytics dashboard with role filtering
- CSV export for cleaned data
- Manual data generation for testing

**Limitations**:

- No persistent storage (data resets on app restart)
- Single-user concurrent access
- No authentication or user management
- Limited to CSV file format

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
