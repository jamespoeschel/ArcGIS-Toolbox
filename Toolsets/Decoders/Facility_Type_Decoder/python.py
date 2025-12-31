import arcpy

# Script tool parameters
in_layer = arcpy.GetParameterAsText(0)  # Input feature layer
input_field = arcpy.GetParameterAsText(1)  # Field with facility type codes

# Mapping from code to description
facility_type_dict = {
    "1": "One-Way Roadway",
    "2": "Two-Way Roadway",
    "3": "One-Way Couplets",
    "4": "Ramp",
    "5": "Non-Mainline",
    "6": "Non-Inventory Direction",
    "7": "Planned/Unbuilt"
}

# Target output field
output_field = "Facility_Type"

# Add field if it doesn't exist
existing_fields = [f.name for f in arcpy.ListFields(in_layer)]
if output_field not in existing_fields:
    arcpy.AddMessage(f"Adding field: {output_field}")
    arcpy.AddField_management(in_layer, output_field, "TEXT", field_length=50)
else:
    arcpy.AddMessage(f"Field '{output_field}' already exists. Overwriting values...")

# Update field values
with arcpy.da.UpdateCursor(in_layer, [input_field, output_field]) as cursor:
    for row in cursor:
        raw_code = row[0]

        # Set output as NULL for 0 or null values
        if raw_code in (None, 0, "0", "0.0"):
            row[1] = None
        else:
            code_str = str(raw_code).strip()
            row[1] = facility_type_dict.get(code_str, "Unknown")

        cursor.updateRow(row)

arcpy.AddMessage("Facility_Type field populated successfully.")
