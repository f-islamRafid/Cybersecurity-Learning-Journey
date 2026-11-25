# File Integrity Monitor

A Python-based cybersecurity tool that monitors file integrity using SHA-256 cryptographic hashing.

The tool creates a baseline of file hashes and compares subsequent scans against that baseline to identify modified, newly created, and deleted files.

## Features

- SHA-256 file hashing
- Baseline creation and storage
- Modified file detection
- New file detection
- Deleted file detection
- JSON baseline storage
- Automated integrity reports
- UTC timestamps
- Baseline validation and error handling
- Atomic baseline file replacement

## Technologies

- Python 3
- hashlib
- JSON
- pathlib
- tempfile
- datetime

## Project Structure

```text
File-Integrity-Monitor/
├── test_files/
│   ├── config.txt
│   ├── notes.txt
│   └── users.txt
├── reports/
├── monitor.py
├── README.md
└── .gitignore
```

## Requirements

- Python 3.10 or newer
- No external Python packages required

## Usage

Run the program:

```bash
python3 monitor.py
```

### Option 1: Create Baseline

Records the current SHA-256 hashes of files inside `test_files/`.

The baseline is saved to:

`reports/baseline.json`

### Option 2: Verify File Integrity

Compares current file hashes against the saved baseline.

The program identifies:

- Modified files
- Newly created files
- Deleted files

The generated report is saved to:

`reports/integrity_report.txt`

## Example Output

```text
FILE INTEGRITY MONITOR REPORT

Modified files: 1
New files: 0
Deleted files: 0

[MODIFIED] config.txt
```

## Security Notes

- The project uses SHA-256 for file integrity checking.
- The baseline should be protected from unauthorized modification.
- This tool is designed for educational and defensive security purposes.
- Only monitor files and directories you are authorized to access.
- A matching hash does not establish that a file is trustworthy; it only indicates that its contents match the recorded baseline.

## Limitations

- Monitoring is performed when the user runs a scan; it is not continuous.
- The baseline is stored locally and is not independently authenticated.
- Symbolic links are skipped.
- Individual unreadable-file reporting is not implemented yet.

## Author

Cybersecurity Learning Project
