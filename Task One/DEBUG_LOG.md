# DEBUG_LOG.md — AI-Assisted Debugging of process_data.py

## Step 1: Understanding the Codebase

### Prompt
> "This is a legacy Python script. Please provide a high-level summary of what it's supposed to do. Then, break down your explanation function by function, detailing the purpose of each, its expected inputs and outputs, and any side effects. Finally, identify any potential areas of concern or parts of the code that seem overly complex or inefficient."

### AI Response (Summary)
The script is a **Customer Analytics Data Processor**. It:
1. Loads customer data from a CSV (`customers.csv`)
2. Processes transaction data from another CSV (`transactions.csv`)
3. Calculates metrics (revenue, top customers, category breakdowns)
4. Generates JSON reports
5. Exports customer data in CSV or JSON format

**Function-by-function breakdown:**

| Function | Purpose | Inputs | Outputs | Side Effects |
|---|---|---|---|---|
| `__init__` | Initialise processor | `input_file` path | None | Sets instance attributes |
| `load_data` | Load customers from CSV | None (uses `self.input_file`) | `bool` | Populates `self.customers` |
| `process_transactions` | Parse transactions, update customer totals | `transaction_file` path | `bool` | Populates `self.transactions`, updates `self.customers` |
| `calculate_customer_metrics` | Compute analytics | None | `Dict` of metrics | None |
| `find_matches` | Search customers by field | `search_term`, `field` | `List[Dict]` | None |
| `generate_report` | Write JSON reports | `report_type`, `output_file` | `bool` | Writes file to disk |
| `export_customer_data` | Export customers as CSV/JSON | `output_file`, `format` | `bool` | Writes file to disk |

**Areas of concern identified:**
1. `export_customer_data` uses `format` as parameter name — **shadows Python built-in**
2. No input validation on CSV rows (missing fields would cause `KeyError`)
3. No validation that `self.customers` values are proper dicts before calling `.keys()`
4. Category breakdown uses manual `if key not in dict` pattern instead of `dict.get()` or `collections.Counter`

### My Thought Process
The code is reasonably structured but lacks defensive programming. The `export_customer_data` function stood out immediately as the likely problem area given it's the last operation in the pipeline.

---

## Step 2: Diagnosing the Bug

### Prompt
> "Given the following function `export_customer_data` and the error log showing `ERROR - Error exporting data: 'dict' object has no attribute 'keys'`, what is the most likely root cause of the failure?"

### Error Log
```
2024-01-15 02:30:16,123 - INFO - Exported customer data to customers_export.csv
2024-01-15 02:30:16,234 - ERROR - Error exporting data: 'dict' object has no attribute 'keys'
```

### AI Response (Summary)
The error occurs on the **second call** to `export_customer_data` (JSON export, after CSV export succeeded). The root cause is:

1. **Line `next(iter(self.customers.values())).keys()`** — If any customer entry in `self.customers` is not a proper dict (e.g., a string or None due to corrupted data), calling `.keys()` will raise `AttributeError`.
2. The error message `'dict' object has no attribute 'keys'` is misleading — it actually means a value that was *expected* to be a dict doesn't have the `.keys()` method, indicating **corrupted customer data** where a non-dict value was stored.
3. Additionally, the parameter `format` shadows Python's built-in, which is a code smell.

### My Thought Process
The CSV export (first call) succeeded, so the data was mostly valid. The JSON export fails because `json.dump` encounters non-serialisable or unexpected data. The lack of any type-checking on `self.customers` values is the vulnerability.

---

## Step 3: Writing a Test to Replicate the Bug

### Prompt
> "Based on your analysis of the bug, write a Python unit test using the 'unittest' library that is specifically designed to fail in the same way the error log shows. This test should call the problematic function with data that triggers the bug."

### AI Response
The AI generated `TestExportCustomerDataBug` which injects a corrupted entry (`"C002": "corrupted_data"`) into `self.customers` and then calls `export_customer_data`. Against the **original** code, this test triggers the same `AttributeError`. Against the **fixed** code, the test passes because corrupted entries are filtered out.

### Test Execution (before fix)
```
FAIL — AttributeError: 'str' object has no attribute 'keys'
```

### My Thought Process
I needed a test that would reliably crash the original code. Injecting a non-dict value into the customers dict was the simplest way to reproduce the exact error.

---

## Step 4: Refactoring and Fixing

### Prompt
> "Refactor the `export_customer_data` function to fix the bug. Rename the `format` parameter to `output_format` to avoid shadowing the built-in. Add isinstance checks to filter out corrupted non-dict customer entries. Also improve `calculate_customer_metrics` to use `dict.get()` instead of manual key existence checks."

### Changes Made
1. **Renamed** `format` → `output_format` in `export_customer_data`
2. **Added** `isinstance(data, dict)` checks before accessing `.keys()` in CSV export
3. **Added** filtering of non-dict entries in JSON export
4. **Added** `row.get()` with defaults in `load_data` and `process_transactions` for defensive input handling
5. **Replaced** manual category breakdown logic with `dict.get()` pattern
6. **Added** `default=str` to `json.dump` calls to handle non-serialisable types
7. **Added** docstrings to all functions

### Test Execution (after fix)
```
Ran 15 tests in 0.02s — OK
```

### My Thought Process
The fix needed to be minimal but robust. Adding `isinstance` guards ensures the code won't crash on corrupted data, while renaming `format` follows Python best practices (PEP 8).

---

## Step 5: Summary

| Step | Action | Outcome |
|---|---|---|
| 1 | Understood codebase with AI | Identified 4 areas of concern |
| 2 | Diagnosed bug using error log | Root cause: missing type validation in `export_customer_data` |
| 3 | Wrote failing unit test | Confirmed bug is reproducible |
| 4 | Refactored and fixed | All 15 tests pass |
| 5 | Documented process | This file |
