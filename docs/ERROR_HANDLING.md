# Error Handling Guide

This guide documents common errors you may encounter when using Community Pulse and their solutions.

---

## Common Errors

### "No Data Generated Yet"

**Cause:** No data has been generated or uploaded in this browser session yet. Data is kept per session in memory, never in a file, so a new session starts empty.

**Solution:**

1. Navigate to the sidebar in the application
2. Adjust the number of records and messiness level if needed
3. Click the **"Generate New Data"** button, or switch **Data Source** to **Upload CSV** and choose a file

---

### Upload rejected in the sidebar

The sidebar checks an upload in the order of this table. The first three stop at the first failure; the last three are checked together, so one upload can show several of them.

| Message                                                    | Cause                                                       | Solution                                              |
| ---------------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------- |
| The uploader refuses the file as too large                 | The file is over 5 MB                                       | Split the file or drop columns you do not need        |
| `Too many columns: uploads are limited to 50 columns.`     | The header has more than 50 fields                          | Drop the columns you do not need                      |
| `Error reading file. Please ensure it is a valid CSV.`     | pandas could not parse the file (the details line says why) | Open it in a spreadsheet and save it again as CSV     |
| `Missing required columns: Join_Date, Event_Attendance`    | Column names are missing or spelled differently             | Rename the columns (see below)                        |
| `... The header looks semicolon-delimited; re-save the file with commas as the delimiter.` | The file uses semicolons, tabs or pipes | Re-save it as a comma-separated CSV             |
| `Row count exceeds limit (50,000).`                        | More than 50,000 data rows                                  | Split the file                                        |

**Required columns** (names are case-sensitive): `Name`, `Email`, `Role`, `Join_Date`, `Event_Attendance`. Other columns are allowed and kept.

---

### ValueError: messiness_level must be 'low', 'medium', or 'high'

**Cause:** Incorrect parameter passed to the data generator function.

**Solution:** Use only the following valid messiness levels:

- `'low'` - Minimal data quality issues
- `'medium'` - Moderate data quality issues (recommended)
- `'high'` - Severe data quality issues

**Example:**

```python
from utils.data_generator import generate_messy_data

# Correct usage
generate_messy_data(500, messiness_level="medium")

# Incorrect usage: raises ValueError("messiness_level must be 'low', 'medium', or 'high', got 'extreme'")
generate_messy_data(500, messiness_level="extreme")
```

A `num_records` that is not a positive integer raises `ValueError: num_records must be a positive integer, got ...` the same way.

---

### "Cleaning removed every record"

**Cause:** Every row was dropped by **Fix Email Formats**, which removes rows whose email is blank or invalid. It is the only step that can drop every row: **Remove Duplicates** keeps the first row of each group.

**Solution:** Turn off the step the warning names in the sidebar's **Configure Cleaning Steps**, or fix the `Email` column, then run the cleaning again.

---

### A chart is empty

**Cause:** The chart's column is missing, or none of its values are usable. The Membership Growth chart needs readable `Join_Date` values (unreadable dates are left out); the attendance histogram needs numeric `Event_Attendance` values; the pie chart needs a `Role` column.

**Solution:** Check those columns in the Data Explorer tab. The Analytics tab shows charts only after cleaning has run; its main charts use the cleaned data.

---

### ModuleNotFoundError: No module named 'package_name'

**Cause:** Required Python package is not installed in your environment.

**Solution:**

```bash
# Activate your virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt

# Or install specific missing package
pip install package_name
```

**Verify installation:**

```bash
python verify_setup.py
```

---

## Testing-Specific Errors

### pytest: command not found

**Cause:** pytest is not installed or not in your PATH.

**Solution:**

```bash
pip install -r requirements-dev.txt
pytest --version  # Verify installation
```

---

### AssertionError in tests

**Cause:** Test expectations don't match actual behavior (likely due to code changes).

**Solution:**

1. Review the specific test that failed
2. Check if the test expectations are still valid
3. Update tests if functionality has intentionally changed
4. Run individual test for debugging: `pytest tests/test_file.py::test_function_name -v`, or `pytest tests/test_file.py::TestClassName::test_function_name -v` for a test inside a class

---

## Deployment Errors

### Streamlit Cloud: requirements.txt missing

**Cause:** Streamlit Cloud cannot find the dependencies file.

**Solution:**

1. Ensure `requirements.txt` is in the repository root
2. Commit and push the file to GitHub
3. Redeploy the application

---

### Streamlit Cloud: Module import error

**Cause:** Package version mismatch or missing system dependencies.

**Solution:**

1. Keep the exact pins in `requirements.txt` (`pandas==2.3.3`, `numpy==2.2.6`); CI installs from the same file, so a green CI run means those versions work together
2. Check Streamlit Cloud logs for specific error messages
3. Ensure Python version compatibility (3.10+, as `requires-python` in `pyproject.toml` says)

---

## Getting Help

If you encounter an error not listed here:

1. **Check the logs:** Review terminal output or Streamlit Cloud logs
2. **Search Issues:** Check the [GitHub Issues](https://github.com/hilliersmmain/community-pulse/issues) page
3. **Create an Issue:** Provide:
   - Error message (full traceback)
   - Steps to reproduce
   - Your environment (OS, Python version)
   - Expected vs. actual behavior

---

## Where Errors Show

There is no debug mode or log-level setting: the application code reads no environment variables. When generating data or running the cleaning fails, the page shows a short message with the technical text in an **Error Details** expander; an upload that cannot be read shows a `Details:` line under the sidebar error. Anything else appears as a traceback in the terminal running `streamlit run app.py`, or in the Streamlit Cloud logs.

---

## Prevention Best Practices

1. **Always use virtual environments:** Prevents package conflicts
2. **Verify setup after installation:** Run `python verify_setup.py`
3. **Generate data before cleaning:** Follow the workflow order
4. **Keep dependencies updated:** Regularly run `pip install --upgrade -r requirements.txt`
5. **Run tests before deployment:** `pytest` to catch issues early
