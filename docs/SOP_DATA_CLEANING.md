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
4. **Important**: Ensure the export includes the required fields `Name`, `Email`, `Role`, `Join_Date`, `Event_Attendance` (the event registration columns `Event_Registered` and `Registration_Date` are optional)
5. Save the file locally (e.g., `raw_member_export_YYYY-MM-DD.csv`)

### Step 2: Upload Data to Community Pulse

1. Open the Community Pulse application
2. If using sample data first, leave **Data Source** on **Generate Sample** in the sidebar and click **"Generate New Data"**
3. For real data: set **Data Source** to **Upload CSV** in the sidebar and choose the file
4. Ensure your CSV includes the required columns, spelled exactly: `Name`, `Email`, `Role`, `Join_Date`, `Event_Attendance`
5. Uploads are limited to 5 MB, 50 columns and 50,000 rows, and must be comma-delimited
6. A good upload shows "Uploaded N records successfully." in the sidebar

The data is kept in your browser session only; nothing is written to the server's disk. Download anything you want to keep (Step 5).

### Step 3: Run Automated Cleaning

1. Review the initial data quality metrics in the **Key Performance Indicators** row at the top of the page:
   - Total Records
   - Duplicate Records
   - Missing Values
2. Optionally choose the steps under **Cleaning Pipeline > Configure Cleaning Steps** in the sidebar (all five are on by default)
3. Navigate to the **"Data Preparation"** tab
4. Click the **"Run Cleaning Algorithms"** button
5. Wait for the "Data cleaning completed successfully! N records processed." notification

### Step 4: Review Cleaning Log

1. Check the **Execution Log** that appears after cleaning
2. Verify the following operations were performed (one log line each):
   - `Standardized Names to Title Case.`
   - `Fixed email formatting. Removed N invalid emails.`
   - `Removed N duplicate rows.`
   - `Standardized Dates. ...` (it says how many unreadable dates were left blank)
   - `Filled N missing Attendance records with 0.`
3. Review the **Records Removed** metric in the Cleaning Summary to understand data quality impact
4. Compare the **Before vs. After Cleaning Comparison** tiles that now appear above the tabs

### Step 5: Download Cleaned Data

1. In the sidebar, go to **Export Options** and set **Export data:** to **Cleaned Data**
2. Click **"Download CSV (Cleaned)"** (or **"Download JSON (Cleaned)"**)
3. The file is named `community_data_cleaned_YYYYMMDD_HHMMSS.csv`; rename it if you like (e.g., `cleaned_members_YYYY-MM-DD.csv`)
4. **Backup**: Store the original raw file and cleaned file in separate folders

### Step 6: Import to CRM or Use for Reporting

1. **Option A** (CRM Re-import): Use the cleaned CSV to update your CRM system
2. **Option B** (Reporting): Use the Analytics tab to visualize insights
3. Document any issues or anomalies discovered during the process

---

## Data Quality Rules

The cleaning pipeline applies the following rules automatically:

| Issue Type             | Detection Method                                                    | Resolution                                       | Impact                             |
| ---------------------- | ------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------- |
| **Inconsistent Names** | Name written entirely in UPPER or lower case                        | Convert to Title Case; mixed-case names are kept | Ensures professional appearance    |
| **Invalid Emails**     | After lower-casing and turning " at " into "@", not a valid address | Remove entire record (also when Email is blank)  | Prevents communication failures    |
| **Duplicate Records**  | Same Email, ignoring case and surrounding spaces                    | Keep first occurrence, remove rest               | Eliminates overcounting in reports |
| **Date Format Issues** | `Join_Date` in ISO, MM/DD/YYYY or DD-MM-YYYY form                   | Parse to a date; unreadable values left blank    | Enables accurate timeline analysis |
| **Missing Attendance** | Blank or non-numeric `Event_Attendance`                             | Fill with 0                                      | Prevents chart rendering errors    |

The rules run in the order shown. Only the columns named here are changed: `Last_Login` and `Registration_Date` keep their original values and gaps.

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

| Problem                                     | Likely Cause                                | Solution                                                                  |
| ------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------- |
| "No Data Generated Yet" panel               | No data loaded in this browser session yet  | Click "Generate New Data" or upload a CSV                                 |
| Large number of records removed             | High duplicate rate or many invalid emails  | Review raw data source for systemic issues                                |
| "Missing required columns: ..." on upload   | Column names differ from the required ones  | Ensure CSV has Name, Email, Role, Join_Date, and Event_Attendance columns |
| "... The header looks semicolon-delimited"  | File saved with semicolons (or tabs, pipes) | Re-save the file with commas as the delimiter                             |
| File refused as too large, or "Too many columns" | Over 5 MB, or more than 50 columns     | Split the file, or drop the columns you do not need                       |
| "Cleaning removed every record" warning     | Every row had an invalid or missing email   | Turn off "Fix Email Formats", or fix the Email column                     |
| Dates show as "NaT" after cleaning          | Date in a form the parser cannot read       | Expected: unreadable dates are left blank, not guessed. Check CRM export settings |

---

## Document Control

- **Version**: 1.1
- **Last Updated**: November 2026
- **Owner**: Data Operations Team
- **Review Cycle**: Quarterly
