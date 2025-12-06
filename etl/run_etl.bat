@echo off
REM Helper script to run the ETL process
REM Usage: run_etl.bat input_file.csv [output_file.csv]

C:\Python312\python.exe process_csv.py %*

