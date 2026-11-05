# Key Performance Indicator (KPI) Definitions

## Overview

This document defines the data quality metrics the Community Pulse dashboard shows. Every number here is computed by `DataHealthMetrics` in `utils/health_metrics.py`; the weights and thresholds live in `utils/constants.py`. Change a constant there, not a number in this file.

The KPI row at the top of the page scores the data in the **current view**: raw data, or cleaned data once cleaning has run and the sidebar's "Current view" is set to Cleaned Data. The four scores (5 to 8 below) also appear in the Data Explorer tab's "Data Health Overview".

---

## Count Metrics

### 1. Total Records

**Definition**: The number of rows in the dataset, duplicates included.

**Source**: `get_detailed_metrics()["total_records"]`

### 2. Duplicate Records

**Definition**: The number of rows whose Email, lower-cased and stripped of surrounding spaces, already appeared in an earlier row. The first row of each group is not counted. Rows with a missing email are never counted as duplicates. A dataset without an `Email` column falls back to counting whole identical rows.

**Source**: `get_detailed_metrics()["duplicate_records"]`, from `duplicate_mask()` in `utils/duplicates.py`. The cleaner's "Remove Duplicates" step uses the same function, so run on its own it removes exactly this many rows. In the full pipeline it can remove more than the raw count shows, because "Fix Email Formats" runs first and repairs addresses such as "ann at x.com", which can then match an earlier row.

### 3. Unique Records

**Formula**:

```
Unique Records = Total Records - Duplicate Records
```

**Source**: `get_detailed_metrics()["unique_records"]`

### 4. Missing Values

**Definition**: The number of empty (null/NaN) cells across every column of the dataset.

**Source**: `get_detailed_metrics()["null_cells"]`

Some columns are blank by design and no cleaning step fills them: `Last_Login` has gaps, and `Registration_Date` is blank whenever a member has no registration. So Missing Values rarely reaches 0 on the generated data, even after cleaning.

The Duplicate Records and Missing Values tiles show the count for the current view only, with no up or down arrow. The before/after change is shown in the "Before vs. After Cleaning Comparison" section that appears once cleaning has run.

---

## Score Metrics (0-100%)

Each score is shown rounded to one decimal place.

### 5. Completeness Score

**Definition**: The share of all cells that are not empty.

**Formula**:

```
Completeness = (Total Cells - Missing Values) / Total Cells × 100
```

`Total Cells` is rows × columns. An empty dataset scores 0%.

**Method**: `calculate_completeness_score()`

### 6. Duplicate Score (shown as "Uniqueness" in the Data Explorer)

**Definition**: The share of rows that are not duplicates, using the Duplicate Records rule above.

**Formula**:

```
Duplicate Score = (Total Records - Duplicate Records) / Total Records × 100
```

An empty dataset scores 100%.

**Method**: `calculate_duplicate_score()`

### 7. Formatting Score

**Definition**: The average validity of the columns that have a format check. A column is checked when its name matches an entry in `FORMATTING_VALIDATORS` (`utils/health_metrics.py`); the first match wins:

| Column name matches          | Check                                                                   |
| ---------------------------- | ----------------------------------------------------------------------- |
| `Email`, or ends in `_email` | Fully matches `EMAIL_PATTERN` (`utils/constants.py`)                    |
| a `date` word, e.g. `Join_Date`, `Registration_Date` | Readable by `parse_dates` (ISO, MM/DD/YYYY, DD-MM-YYYY, and other forms pandas can read) |
| `Name`, or ends in `_name`   | Fully matches `NAME_PATTERN`: letters of any script, spaces, apostrophes, full stops, hyphens |
| `ID`, or ends in `_id`       | Not blank                                                               |

Name matching ignores case. Only non-empty cells are checked; empty cells count against Completeness instead. Each checked column scores the percentage of its values that pass, and the Formatting Score is the plain average of those column scores. Columns with no check (for the generated data: `Last_Login`, `Event_Attendance`, `Role`, `Event_Registered`) are left out of the average. A dataset that is empty, or has no checked column, scores 100%.

**Method**: `calculate_formatting_score()`

### 8. Data Health Score

**Definition**: A weighted average of the three scores above.

**Formula**:

```
Data Health Score = (0.4 × Completeness) + (0.3 × Duplicate Score) + (0.3 × Formatting)
```

The weights are `HEALTH_SCORE_WEIGHT_COMPLETENESS` (0.4), `HEALTH_SCORE_WEIGHT_UNIQUENESS` (0.3) and `HEALTH_SCORE_WEIGHT_FORMATTING` (0.3) in `utils/constants.py`. Because an empty dataset scores 0% Completeness and 100% on the other two, it gets a Data Health Score of 60%.

**Interpretation** (`SCORE_THRESHOLDS` in `utils/constants.py`):

- **90% and above**: Excellent
- **70% to under 90%**: Good
- **Below 70%**: Needs Work

**Method**: `calculate_overall_health_score()`

---

## Before vs. After Cleaning

After "Run Cleaning Algorithms", the dashboard adds a "Before vs. After Cleaning Comparison" section with four pairs of tiles: Records, Duplicates, Missing Values and Health Score. "Before" scores the raw data and "After" scores the cleaned data, with the change shown under "After". The Data Preparation tab's "Cleaning Summary" also shows Records Removed and the cleaned Data Health Score with its change.

---

## Charts

The Analytics tab's main charts use the cleaned data (its Before/After Cleaning Visual Comparison section adds the raw-data versions); they are views of the data, not KPIs:

- **Membership Growth Over Time**: new members per month from `Join_Date`, with a straight-line trend and the mean.
- **Event Attendance Distribution**: a histogram of `Event_Attendance` with mean and median lines.
- **Member Role Distribution**: a pie chart of `Role`.

The Role filter on the Analytics tab narrows these charts. It does not change the KPI row.
