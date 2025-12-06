# CSV Import Format Guide

## Required Columns

The following columns are **mandatory** and must be present in your CSV file:

1. **Customer Number** - Unique identifier for the customer
2. **Passenger Name** - Name of the passenger/client
3. **Trip Date** - Date of the trip (format: YYYY-MM-DD or similar)
4. **Promised pick-up time** - Scheduled pickup time (format: HH:MM or HH:MM:SS)
5. **Pickup street number** - Street number of pickup location
6. **Pickup Street** - Street name of pickup location
7. **Pickup City** - City of pickup location
8. **Promised drop-off time** - Scheduled dropoff time (format: HH:MM or HH:MM:SS)
9. **Drop-off street number** - Street number of dropoff location
10. **Drop-off Street** - Street name of dropoff location
11. **Drop-off City** - City of dropoff location

## Optional Columns

The following columns are **optional** but can be included:

1. **Mobility Needs** - Special mobility requirements or notes
2. **Special Notes** - Any additional notes or instructions
3. **Hard Driver Constraints** - Comma-separated list of driver IDs that must or must not be assigned (format: "DRIVER1,DRIVER2" or "-DRIVER3" to exclude)

## Column Name Format

**Important**: Column names are case-sensitive and must match exactly:

- ✅ `Customer Number` (with space)
- ✅ `Passenger Name` (with space)
- ✅ `Trip Date` (with space)
- ✅ `Promised pick-up time` (with space and hyphen)
- ✅ `Pickup street number` (lowercase "street number")
- ✅ `Pickup Street` (capitalized "Street")
- ✅ `Pickup City` (capitalized "City")
- ✅ `Promised drop-off time` (with space and hyphen)
- ✅ `Drop-off street number` (lowercase "street number")
- ✅ `Drop-off Street` (capitalized "Street")
- ✅ `Drop-off City` (capitalized "City")
- ✅ `Mobility Needs` (with space)
- ✅ `Special Notes` (with space)
- ✅ `Hard Driver Constraints` (with spaces)

## CSV Example

```csv
Customer Number,Passenger Name,Trip Date,Promised pick-up time,Pickup street number,Pickup Street,Pickup City,Promised drop-off time,Drop-off street number,Drop-off Street,Drop-off City,Mobility Needs,Special Notes
12345,John Doe,2024-12-15,08:30,123,Main Street,Springfield,09:00,456,Oak Avenue,Springfield,Wheelchair,Patient requires assistance
12346,Jane Smith,2024-12-15,10:00,789,Elm Street,Springfield,10:30,789,Elm Street,Springfield,,""
```

## Date and Time Formats

### Trip Date
- Format: `YYYY-MM-DD` (e.g., `2024-12-15`)
- Alternative formats may work but `YYYY-MM-DD` is recommended

### Time Fields
- **Promised pick-up time**: `HH:MM` (e.g., `08:30`) or `HH:MM:SS` (e.g., `08:30:00`)
- **Promised drop-off time**: `HH:MM` (e.g., `09:00`) or `HH:MM:SS` (e.g., `09:00:00`)

## Validation Rules

1. **Required Fields**: All mandatory columns must have values (cannot be empty)
2. **Date Format**: Trip Date must be a valid date
3. **Time Format**: Time fields must be valid time format if provided
4. **Address Fields**: Pickup and dropoff address components cannot be empty

## Error Messages

If validation fails, you'll see errors like:
- `Row X, Field 'Customer Number': Field is required and cannot be empty`
- `Row X, Field 'Trip Date': Invalid date format: ...`
- `Row X, Field 'Promised pick-up time': Invalid time format: ...`

## Tips

1. **Save as CSV**: Make sure your file is saved as `.csv` format (not Excel `.xlsx`)
2. **UTF-8 Encoding**: Use UTF-8 encoding to avoid character issues
3. **No Headers Row**: The first row should contain column headers
4. **Consistent Formatting**: Keep date and time formats consistent throughout
5. **Empty Optional Fields**: You can leave optional columns empty or omit them entirely

## Sample CSV Template

You can copy this template and fill in your data:

```csv
Customer Number,Passenger Name,Trip Date,Promised pick-up time,Pickup street number,Pickup Street,Pickup City,Promised drop-off time,Drop-off street number,Drop-off Street,Drop-off City,Mobility Needs,Special Notes
```

## Import Process

1. Go to "Import Clients" page in the application
2. Select the service date (must match the Trip Date in your CSV)
3. Click "Browse..." and select your CSV file
4. Click "Import CSV"
5. Review validation errors if any
6. Check the imported trips preview

## Notes

- The system will automatically geocode addresses (convert to coordinates) using Google Maps API
- Geocoding results are cached to reduce API calls
- Invalid rows will be reported but won't prevent valid rows from being imported
- All successfully imported trips will be marked as "ready_for_scheduling"


