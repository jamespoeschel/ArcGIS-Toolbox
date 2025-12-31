# Contributors: James Poeschel
import arcpy

# Get input parameters
Layer_Name = arcpy.GetParameterAsText(0)
State_Name_Field = arcpy.GetParameterAsText(1)
FIPS_Code_Field = arcpy.GetParameterAsText(2)

# State Name -> FIPS mapping (zero-padded for text fields)
state_to_fips_text = {
    'ALABAMA': '01', 'ALASKA': '02', 'ARIZONA': '04', 'ARKANSAS': '05',
    'CALIFORNIA': '06', 'COLORADO': '08', 'CONNECTICUT': '09', 'DELAWARE': '10',
    'DISTRICT OF COLUMBIA': '11', 'FLORIDA': '12', 'GEORGIA': '13',
    'HAWAII': '15', 'IDAHO': '16', 'ILLINOIS': '17', 'INDIANA': '18',
    'IOWA': '19', 'KANSAS': '20', 'KENTUCKY': '21', 'LOUISIANA': '22',
    'MAINE': '23', 'MARYLAND': '24', 'MASSACHUSETTS': '25',
    'MICHIGAN': '26', 'MINNESOTA': '27', 'MISSISSIPPI': '28',
    'MISSOURI': '29', 'MONTANA': '30', 'NEBRASKA': '31', 'NEVADA': '32',
    'NEW HAMPSHIRE': '33', 'NEW JERSEY': '34', 'NEW MEXICO': '35',
    'NEW YORK': '36', 'NORTH CAROLINA': '37', 'NORTH DAKOTA': '38',
    'OHIO': '39', 'OKLAHOMA': '40', 'OREGON': '41', 'PENNSYLVANIA': '42',
    'RHODE ISLAND': '44', 'SOUTH CAROLINA': '45', 'SOUTH DAKOTA': '46',
    'TENNESSEE': '47', 'TEXAS': '48', 'UTAH': '49', 'VERMONT': '50',
    'VIRGINIA': '51', 'WASHINGTON': '53', 'WEST VIRGINIA': '54',
    'WISCONSIN': '55', 'WYOMING': '56',
    'AMERICAN SAMOA': '60', 'GUAM': '66', 'NORTHERN MARIANA ISLANDS': '69',
    'PUERTO RICO': '72', 'U.S. VIRGIN ISLANDS': '78', 'US VIRGIN ISLANDS': '78'
}

# Determine if FIPS field is text
fips_field = arcpy.ListFields(Layer_Name, FIPS_Code_Field)[0]
is_text_field = fips_field.type in ('String', 'Text')

# Update FIPS field using state name
with arcpy.da.UpdateCursor(Layer_Name, [State_Name_Field, FIPS_Code_Field]) as cursor:
    for row in cursor:
        state = row[0]
        if state:
            key = state.strip().upper()
            fips_val = state_to_fips_text.get(key)
            if fips_val:
                if not is_text_field:
                    fips_val = int(fips_val)  # convert to int if field is numeric
                row[1] = fips_val
            else:
                row[1] = None  # no match
        else:
            row[1] = None  # empty state name
        cursor.updateRow(row)
