# ETL Module

This module handles the Extract, Transform, Load (ETL) process for ingesting CSV files and preparing data for schedule generation.

## Usage

### Basic Usage

**Windows (using Python at C:\Python312):**
```bash
# Option 1: Use the helper script
run_etl.bat input_file.csv

# Option 2: Use full path
C:\Python312\python.exe process_csv.py input_file.csv
```

**If Python is in your PATH:**
```bash
python process_csv.py input_file.csv
```

### With Output File

**Windows:**
```bash
run_etl.bat input_file.csv output_file.csv
# or
C:\Python312\python.exe process_csv.py input_file.csv output_file.csv
```

**If Python is in your PATH:**
```bash
python process_csv.py input_file.csv output_file.csv
```

## Functions

- `load_csv()`: Loads CSV file into pandas DataFrame
- `validate_data()`: Validates and cleans input data
- `transform_data()`: Transforms data according to scheduling requirements
- `process_csv()`: Main ETL pipeline

## Requirements

### Installation

**Windows (using Python at C:\Python312):**
```bash
# Option 1: Use the helper script
install.bat

# Option 2: Use full path
C:\Python312\python.exe -m pip install --user -r requirements.txt
```

**If Python is in your PATH:**
```bash
pip install -r requirements.txt
# or
python -m pip install -r requirements.txt
```

## Status

🚧 Awaiting detailed requirements to implement specific transformation logic

