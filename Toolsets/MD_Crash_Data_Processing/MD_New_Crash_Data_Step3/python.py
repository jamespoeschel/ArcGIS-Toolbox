import arcpy
import os

# Get input parameters
crashData = arcpy.GetParameterAsText(0)  # Path to the input crash data
output_feature = arcpy.GetParameterAsText(1)  # Output feature class name

# Get the project's home geodatabase
home_gdb = arcpy.mp.ArcGISProject("CURRENT").defaultGeodatabase

# Define fields
occupant_fields = {
    "Fatalities": "Occupant_Fatalities",
    "Severe_Injuries": "Occupant_Severe_Injuries",
    "Minor_Injuries": "Occupant_Minor_Injuries",
    "Possible_Injuries": "Occupant_Possible_Injuries",
    "Property_Damage_Only": "Occupant_PDO"
}

nonmotorist_fields = {
    "Fatalities": "NonMotorist_Fatalities",
    "Severe_Injuries": "NonMotorist_Severe_Injuries",
    "Minor_Injuries": "NonMotorist_Minor_Injuries",
    "Possible_Injuries": "NonMotorist_Possible_Injuries",
    "Property_Damage_Only": "NonMotorist_PDO"
}

# New Total Fields
total_fields = {
    "Fatalities": "Total_Fatalities",
    "Severe_Injuries": "Total_Severe_Injuries",
    "Minor_Injuries": "Total_Minor_Injuries",
    "Possible_Injuries": "Total_Possible_Injuries",
    "Property_Damage_Only": "Total_PDO"
}

# Add new Total fields if they don't already exist
arcpy.AddMessage("Adding total fields...")
existing_fields = [f.name for f in arcpy.ListFields(crashData)]
for total_field in total_fields.values():
    if total_field not in existing_fields:
        arcpy.AddField_management(crashData, total_field, "LONG")

# Add Detailed_Report_Type field if it doesn't already exist
detailed_field = "Detailed_Report_Type"
if detailed_field not in existing_fields:
    arcpy.AddField_management(crashData, detailed_field, "TEXT", field_length=50)

# Update totals for each severity type and determine Detailed_Report_Type
arcpy.AddMessage("Calculating totals and Detailed_Report_Type...")

# Define cursor fields (input + output fields + detailed field)
cursor_fields = (
    list(occupant_fields.values()) +
    list(nonmotorist_fields.values()) +
    list(total_fields.values()) +
    [detailed_field]
)

with arcpy.da.UpdateCursor(crashData, cursor_fields) as cursor:
    for row in cursor:
        # Extract values, replacing None with 0
        occupant_fatalities = row[0] if row[0] is not None else 0
        nonmotorist_fatalities = row[5] if row[5] is not None else 0

        occupant_severe = row[1] if row[1] is not None else 0
        nonmotorist_severe = row[6] if row[6] is not None else 0

        occupant_minor = row[2] if row[2] is not None else 0
        nonmotorist_minor = row[7] if row[7] is not None else 0

        occupant_possible = row[3] if row[3] is not None else 0
        nonmotorist_possible = row[8] if row[8] is not None else 0

        occupant_pdo = row[4] if row[4] is not None else 0
        nonmotorist_pdo = row[9] if row[9] is not None else 0

        # Calculate totals
        total_fatalities = occupant_fatalities + nonmotorist_fatalities
        total_severe = occupant_severe + nonmotorist_severe
        total_minor = occupant_minor + nonmotorist_minor
        total_possible = occupant_possible + nonmotorist_possible
        total_pdo = occupant_pdo + nonmotorist_pdo

        # Update row values for totals
        row[10] = total_fatalities  # Total_Fatalities
        row[11] = total_severe      # Total_Severe_Injuries
        row[12] = total_minor       # Total_Minor_Injuries
        row[13] = total_possible    # Total_Possible_Injuries
        row[14] = total_pdo         # Total_Property_Damage_Only

        # Determine Detailed_Report_Type based on hierarchy
        if total_fatalities > 0:
            report_type = "Fatal"
        elif total_severe > 0:
            report_type = "Severe Injury"
        elif total_minor > 0:
            report_type = "Minor Injury"
        elif total_possible > 0:
            report_type = "Possible Injury"
        elif total_pdo > 0:
            report_type = "Property Damage Only"
        else:
            report_type = "Property Damage Only"

        # Update Detailed_Report_Type
        row[15] = report_type  # Index 15 is Detailed_Report_Type

        # Write updated row back
        cursor.updateRow(row)

arcpy.AddMessage("Totals and Detailed_Report_Type calculated successfully.")


"""
# Hide unwanted fields, deleting can cause bugs
arcpy.AddMessage("Hiding unwanted fields...")
fields_to_hide = [
    "NonMotoristID", "OccupantID", "Vehicleid",
    
    # Occupant tally fields
    "Occupant_Fatalities", "Occupant_Severe_Injuries", "Occupant_Minor_Injuries",
    "Occupant_Possible_Injuries", "Occupant_Property_Damage_Only",
    
    # NonMotorist tally fields
    "NonMotorist_Fatalities", "NonMotorist_Severe_Injuries", "NonMotorist_Minor_Injuries",
    "NonMotorist_Possible_Injuries", "NonMotorist_Property_Damage_Only"
]


existing_fields = [f.name for f in arcpy.ListFields(crashData)]
for field in fields_to_hide:
    if field in existing_fields:
        arcpy.DeleteField_management(crashData, field)
        arcpy.AddMessage(f"Hidden field: {field}")
"""



output_path = os.path.join(home_gdb, output_feature)
arcpy.management.CopyFeatures(crashData, output_path)

arcpy.AddMessage("Field cleanup completed successfully.")
