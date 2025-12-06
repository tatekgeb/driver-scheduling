@echo off
REM Helper script to install ETL dependencies
REM Uses the Python installation at C:\Python312

C:\Python312\python.exe -m pip install --user -r requirements.txt

