#!/usr/bin/env python3
"""
ETL Tool for Driver Scheduling System
Processes CSV files and prepares data for schedule generation.
"""

import pandas as pd
import sys
import os
from pathlib import Path


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load CSV file into a pandas DataFrame.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame containing the CSV data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded CSV: {len(df)} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        raise Exception(f"Error loading CSV: {str(e)}")


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean the input data.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Remove duplicate rows
    initial_count = len(df)
    df = df.drop_duplicates()
    removed = initial_count - len(df)
    if removed > 0:
        print(f"Removed {removed} duplicate rows")
    
    # Remove rows with all NaN values
    df = df.dropna(how='all')
    
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the data according to scheduling requirements.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Transformed DataFrame
    """
    # Placeholder for transformation logic
    # This will be implemented based on detailed requirements
    print("Transforming data...")
    
    return df


def process_csv(input_file: str, output_file: str = None) -> pd.DataFrame:
    """
    Main ETL pipeline: Extract, Transform, Load
    
    Args:
        input_file: Path to input CSV file
        output_file: Optional path to save processed data
        
    Returns:
        Processed DataFrame
    """
    print(f"Starting ETL process for: {input_file}")
    
    # Extract
    df = load_csv(input_file)
    
    # Validate
    df = validate_data(df)
    
    # Transform
    df = transform_data(df)
    
    # Load (save if output file specified)
    if output_file:
        df.to_csv(output_file, index=False)
        print(f"Processed data saved to: {output_file}")
    
    return df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_csv.py <input_file.csv> [output_file.csv]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = process_csv(input_file, output_file)
        print(f"\nETL process completed successfully!")
        print(f"Final dataset: {len(result)} rows, {len(result.columns)} columns")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

