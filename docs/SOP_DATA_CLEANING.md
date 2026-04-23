# Standard Operating Procedure: Data Cleaning Workflow

## Purpose

This SOP defines the standardized process for cleaning and preparing member data exported from the CRM system before importing it into the Community Pulse dashboard. Following this procedure ensures data quality, eliminates duplicates, and maintains consistency across all member records.

## When to Use This SOP

- **Frequency**: Weekly or before generating reports
- **Trigger Events**: After bulk data imports, member data updates, or when data quality issues are detected
- **Responsible Party**: Data Administrator or designated staff member

## 6-Step Data Cleaning Workflow

### Step 1: Export Raw Data from CRM

1. Log into your CRM system
2. Navigate to the Members/Contacts section
3. Select "Export to CSV" or equivalent
4. **Important**: Ensure the export includes all required fields:
   - Name, Email, Join Date, Event Attendance, Role, Event Registration details
5. Save the file locally (e.g., `raw_member_export_YYYY-MM-DD.csv`)

### Step 2: Upload Data to Community Pulse

1. Open the Community Pulse application
2. If using sample data first, click **"Generate New Messy Data"** in the sidebar
3. For real data: Use **Upload CSV** in the sidebar
4. Ensure your CSV includes required fields: `Name`, `Email`, `Role`, `Join_Date`, `Event_Attendance`

### Step 3: Run Automated Cleaning

1. Navigate to the **"Data Preparation"** tab
2. Review the initial data quality metrics displayed at the top:
   - Raw Records count
   - Duplicates Detected
   - Missing Values
3. Click the **"Run Cleaning Algorithms"** button
4. Wait for the "Pipeline executed successfully!" message

### Step 4: Review Cleaning Log

1. Check the **Execution Log** that appears after cleaning
2. Verify the following operations were performed:
   - Names standardized to Title Case
   - Email formats fixed (invalid emails removed)
   - Duplicate rows removed
   - Dates standardized
   - Missing attendance values filled
3. Review the **Records Removed** metric to understand data quality impact

### Step 5: Download Cleaned Data

1. Locate the **"📥 Download Cleaned Data (CSV)"** button below the metrics
2. Click to download the cleaned CSV file
3. Save with a descriptive name (e.g., `cleaned_members_YYYY-MM-DD.csv`)
4. **Backup**: Store the original raw file and cleaned file in separate folders

### Step 6: Import to CRM or Use for Reporting

1. **Option A** (CRM Re-import): Use the cleaned CSV to update your CRM system
2. **Option B** (Reporting): Use the Analytics tab to visualize insights
3. Document any issues or anomalies discovered during the process

---

## Data Quality Rules

The cleaning pipeline applies the following rules automatically:

| Issue Type             | Detection Method                                | Resolution                          | Impact                             |
| ---------------------- | ----------------------------------------------- | ----------------------------------- | ---------------------------------- |
| **Duplicate Records**  | Exact match on Email (case-insensitive)         | Keep first occurrence, remove rest  | Eliminates overcounting in reports |
| **Inconsistent Names** | Mixed capitalization (UPPER, lower, Mixed)      | Convert all to Title Case           | Ensures professional appearance    |
| **Invalid Emails**     | Missing "@" symbol or malformed format          | Remove entire record                | Prevents communication failures    |
| **Date Format Issues** | Multiple formats (MM/DD/YYYY, YYYY-MM-DD, etc.) | Parse and standardize to ISO format | Enables accurate timeline analysis |
| **Missing Attendance** | Null/blank Event_Attendance values              | Fill with 0                         | Prevents chart rendering errors    |

---

## Best Practices

✅ **DO:**

- Run this process weekly to maintain data quality
- Keep backup copies of both raw and cleaned data
- Review the cleaning log for unexpected patterns
- Use the Analytics tab to validate results visually

❌ **DON'T:**

- Skip the review step—always check the log
- Delete the raw data file (needed for audit trails)
- Run cleaning on already-cleaned data (creates duplicate work)
- Ignore sudden changes in "Records Removed" counts (investigate first)

---

## Troubleshooting

| Problem                         | Likely Cause                               | Solution                                             |
| ------------------------------- | ------------------------------------------ | ---------------------------------------------------- |
| "No data found" error           | Data file not generated                    | Click "Generate New Messy Data" or upload CSV        |
| Large number of records removed | High duplicate rate or many invalid emails | Review raw data source for systemic issues           |
| Cleaning fails with error       | Missing required columns                   | Ensure CSV has Name, Email, Role, Join_Date, and Event_Attendance columns |
| Dates show as "NaT"             | Unsupported date format                    | Check CRM export settings                            |

---

## Document Control

- **Version**: 1.0
- **Last Updated**: December 2025
- **Owner**: Data Operations Team
- **Review Cycle**: Quarterly
