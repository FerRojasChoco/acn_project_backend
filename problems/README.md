# `process_submission()` Return Schema Documentation

The `process_submission()` function executes every test case inside an isolated sandbox and returns a **list of dictionaries**, where each dictionary describes the result of a single test case execution.

Each test case produces one dictionary with the following structure:

---

## **Schema: Test Case Result Object**

### **`status`** (string)
Represents the final execution state of the submission for the given test case.

Possible values:

| Status | Meaning |
|--------|---------|
| **AC** | Accepted — program ran successfully and output matched the expected result. |
| **WA** | Wrong Answer — program ran successfully but output did NOT match expected result. |
| **RE** | Runtime Error — Python exception occurred in `solution.py`. Includes a sanitized traceback. |
| **MLE** | Memory Limit Exceeded — traceback indicates a memory error (e.g., `MemoryError`, killed due to OOM). |
| **TO** | Time Limit Exceeded — the isolate sandbox reported timeout (`status = "TO"`). |
| **XX** | Internal Sandbox Error — isolate returned an internal error (`status = "XX"`). |

---

## **`mem`** (float)
The peak memory usage of the program during execution, taken from isolate's `max-rss`.

- Represented in **megabytes** (MB).
- Rounded to **2 decimal places**.
- Example: `12.45`

---

## **`time`** (float)
The total execution time of the program.

- Extracted from isolate’s execution metadata.
- Represented in **seconds**.
- Rounded to **3 decimal places**.
- Example: `0.037`

---

## **`traceback`** (string, optional)
This field only appears when:

- `status == "RE"` (Runtime Error)

Contains a **sanitized Python traceback** with:

- Only lines referencing `solution.py`
- The final error message (e.g., `ZeroDivisionError: division by zero`)

Example:

```
File "solution.py", line 4, in solve
ZeroDivisionError: division by zero
```

This field is **not included** for: AC, WA, TO, XX.

---

## **Examples**

### **1. Accepted Test Case**
```json
{
  "mem": 8.12,
  "time": 0.034,
  "status": "AC"
}
```

### **2. Wrong Answer**
```json
{
  "mem": 7.91,
  "time": 0.028,
  "status": "WA"
}
```

### **3. Runtime Error**
```json
{
  "mem": 9.44,
  "time": 0.021,
  "status": "RE",
  "traceback": "File \"solution.py\", line 3, in solve\nZeroDivisionError: division by zero"
}
```

### **4. Memory Limit Exceeded**
```json
{
  "mem": 12.77,
  "time": 0.099,
  "status": "MLE"
}
```

### **5. Time Limit Exceeded**
```json
{
  "mem": 7.33,
  "time": 0.100,
  "status": "TO"
}
```

### **6. Internal Sandbox Error**
```json
{
  "mem": 0.0,
  "time": 0.0,
  "status": "XX"
}
```

---

## **Summary**

Each test case result contains:

| Field        | Type   | Always Present? | Description |
|--------------|--------|------------------|-------------|
| `status`     | string | Yes              | Final test case outcome |
| `mem`        | float  | Yes              | Peak memory usage (MB) |
| `time`       | float  | Yes              | Execution time (s) |
| `traceback`  | string | Only for RE      | Sanitized exception traceback |

The full return value is a **list** of these objects, one for each input file in the `test_cases/` directory.

