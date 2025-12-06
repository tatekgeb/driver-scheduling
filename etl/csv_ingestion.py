"""
Enhanced CSV ingestion module for client trip data
"""
import pandas as pd
import sys
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path

# Add parent directory to path to import shared types
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.types.models import ClientTrip, Address, TripType, TripStatus


class CSVIngestionError(Exception):
    """Custom exception for CSV ingestion errors"""
    pass


class ValidationError:
    """Represents a validation error"""
    def __init__(self, row_number: int, field: str, error_description: str):
        self.row_number = row_number
        self.field = field
        self.error_description = error_description
    
    def __str__(self):
        return f"Row {self.row_number}, Field '{self.field}': {self.error_description}"


class CSVIngester:
    """Handles CSV ingestion and validation"""
    
    # Expected CSV column names
    REQUIRED_COLUMNS = [
        'Customer Number',
        'Passenger Name',
        'Trip Date',
        'Promised pick-up time',
        'Pickup street number',
        'Pickup Street',
        'Pickup City',
        'Promised drop-off time',
        'Drop-off street number',
        'Drop-off Street',
        'Drop-off City'
    ]
    
    OPTIONAL_COLUMNS = [
        'Mobility Needs',
        'Special Notes',
        'Hard Driver Constraints'
    ]
    
    def __init__(self, arrival_buffer_minutes: int = 5):
        self.arrival_buffer_minutes = arrival_buffer_minutes
        self.validation_errors: List[ValidationError] = []
    
    def validate_csv_structure(self, df: pd.DataFrame) -> bool:
        """Validate that CSV has required columns"""
        missing_columns = []
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            raise CSVIngestionError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        return True
    
    def parse_datetime(self, date_str: str, time_str: str = None) -> datetime:
        """Parse date and time strings into datetime object"""
        try:
            if time_str:
                # Combine date and time
                dt_str = f"{date_str} {time_str}"
                return pd.to_datetime(dt_str, errors='raise')
            else:
                return pd.to_datetime(date_str, errors='raise')
        except Exception as e:
            raise ValueError(f"Invalid date/time format: {str(e)}")
    
    def validate_row(self, row: pd.Series, row_number: int) -> List[ValidationError]:
        """Validate a single row and return list of errors"""
        errors = []
        
        # Check required fields are not empty
        for col in self.REQUIRED_COLUMNS:
            if pd.isna(row[col]) or str(row[col]).strip() == '':
                errors.append(ValidationError(
                    row_number, col, "Field is required and cannot be empty"
                ))
        
        # Validate date/time formats
        try:
            trip_date = self.parse_datetime(str(row['Trip Date']))
        except Exception as e:
            errors.append(ValidationError(
                row_number, 'Trip Date', f"Invalid date format: {str(e)}"
            ))
        
        # Validate pickup time if provided
        if not pd.isna(row.get('Promised pick-up time')):
            try:
                pickup_time = self.parse_datetime(
                    str(row['Trip Date']),
                    str(row['Promised pick-up time'])
                )
            except Exception as e:
                errors.append(ValidationError(
                    row_number, 'Promised pick-up time', f"Invalid time format: {str(e)}"
                ))
        
        # Validate dropoff time if provided
        if not pd.isna(row.get('Promised drop-off time')):
            try:
                dropoff_time = self.parse_datetime(
                    str(row['Trip Date']),
                    str(row['Promised drop-off time'])
                )
            except Exception as e:
                errors.append(ValidationError(
                    row_number, 'Promised drop-off time', f"Invalid time format: {str(e)}"
                ))
        
        return errors
    
    def normalize_text(self, text: str) -> str:
        """Normalize text (trim, normalize casing)"""
        if pd.isna(text):
            return ""
        return str(text).strip()
    
    def parse_boolean(self, text: str) -> bool:
        """Parse Yes/No, Y/N, true/false to boolean"""
        if pd.isna(text):
            return False
        text = str(text).strip().upper()
        return text in ['YES', 'Y', 'TRUE', '1']
    
    def create_address(self, row: pd.Series, prefix: str) -> Address:
        """Create Address object from row with given prefix"""
        return Address(
            street_number=self.normalize_text(row[f'{prefix} street number']),
            street=self.normalize_text(row[f'{prefix} Street']),
            city=self.normalize_text(row[f'{prefix} City'])
        )
    
    def row_to_client_trip(self, row: pd.Series, row_number: int) -> ClientTrip:
        """Convert a CSV row to ClientTrip object"""
        # Parse dates/times
        trip_date = self.parse_datetime(str(row['Trip Date']))
        
        promised_pickup = None
        if not pd.isna(row.get('Promised pick-up time')):
            promised_pickup = self.parse_datetime(
                str(row['Trip Date']),
                str(row['Promised pick-up time'])
            )
        
        promised_dropoff = None
        if not pd.isna(row.get('Promised drop-off time')):
            promised_dropoff = self.parse_datetime(
                str(row['Trip Date']),
                str(row['Promised drop-off time'])
            )
        
        # Create addresses
        pickup_address = self.create_address(row, 'Pickup')
        dropoff_address = self.create_address(row, 'Drop-off')
        
        # Determine trip type (for now, assume round trip - will need both pickup and dropoff)
        # This will be expanded to handle both directions
        
        # Parse constraints
        hard_constraints = []
        if not pd.isna(row.get('Hard Driver Constraints')):
            constraints_str = str(row['Hard Driver Constraints']).strip()
            if constraints_str:
                hard_constraints = [c.strip() for c in constraints_str.split(',')]
        
        return ClientTrip(
            trip_id=f"TRIP_{row_number}_{row['Customer Number']}",
            customer_number=str(row['Customer Number']).strip(),
            passenger_name=self.normalize_text(row['Passenger Name']),
            trip_date=trip_date,
            trip_type=TripType.PICKUP,  # Will be determined based on context
            pickup_address=pickup_address,
            dropoff_address=dropoff_address,
            promised_pickup_time=promised_pickup,
            promised_dropoff_time=promised_dropoff,
            appointment_time=promised_dropoff,  # Assuming dropoff time is appointment time
            arrival_buffer_minutes=self.arrival_buffer_minutes,
            mobility_needs=self.normalize_text(row.get('Mobility Needs', '')),
            special_notes=self.normalize_text(row.get('Special Notes', '')),
            hard_driver_constraints=hard_constraints,
            status=TripStatus.IMPORTED
        )
    
    def ingest_csv(self, file_path: str) -> Tuple[List[ClientTrip], List[ValidationError]]:
        """
        Ingest CSV file and return list of ClientTrip objects and validation errors
        
        Returns:
            Tuple of (valid_trips, validation_errors)
        """
        try:
            # Load CSV
            df = pd.read_csv(file_path)
            
            # Validate structure
            self.validate_csv_structure(df)
            
            # Validate and process each row
            valid_trips = []
            all_errors = []
            
            for idx, row in df.iterrows():
                row_number = idx + 2  # +2 because: 0-indexed + 1, plus header row
                errors = self.validate_row(row, row_number)
                
                if errors:
                    all_errors.extend(errors)
                else:
                    try:
                        trip = self.row_to_client_trip(row, row_number)
                        valid_trips.append(trip)
                    except Exception as e:
                        all_errors.append(ValidationError(
                            row_number, 'General', f"Error processing row: {str(e)}"
                        ))
            
            return valid_trips, all_errors
            
        except Exception as e:
            raise CSVIngestionError(f"Failed to ingest CSV: {str(e)}")


def ingest_client_csv(file_path: str, arrival_buffer_minutes: int = 5) -> Tuple[List[ClientTrip], List[ValidationError]]:
    """
    Main function to ingest client CSV file
    
    Args:
        file_path: Path to CSV file
        arrival_buffer_minutes: Arrival buffer in minutes (default 5)
    
    Returns:
        Tuple of (valid_trips, validation_errors)
    """
    ingester = CSVIngester(arrival_buffer_minutes=arrival_buffer_minutes)
    return ingester.ingest_csv(file_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python csv_ingestion.py <input_file.csv>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        trips, errors = ingest_client_csv(file_path)
        
        print(f"\nIngestion Summary:")
        print(f"  Valid trips: {len(trips)}")
        print(f"  Validation errors: {len(errors)}")
        
        if errors:
            print(f"\nValidation Errors:")
            for error in errors:
                print(f"  {error}")
        
        if trips:
            print(f"\nSample trip:")
            print(f"  Customer: {trips[0].customer_number}")
            print(f"  Passenger: {trips[0].passenger_name}")
            print(f"  Date: {trips[0].trip_date}")
            print(f"  Pickup: {trips[0].pickup_address}")
            print(f"  Dropoff: {trips[0].dropoff_address}")
    
    except CSVIngestionError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

