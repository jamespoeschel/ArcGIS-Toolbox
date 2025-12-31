import arcpy

# Script tool parameters
in_layer = arcpy.GetParameterAsText(0)  # Input feature layer
input_field = arcpy.GetParameterAsText(1)  # Field with functional class codes

# Mapping from code to description
code_dict = {
    "1": "Interstate",
    "2": "Other Freeways and Expressways",
    "3": "Other Principal Arterial",
    "4": "Minor Arterial",
    "5": "Major Collector",
    "6": "Minor Collector",
    "7": "Local"
}

# Target output field
output_field = "Functional_Class"

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
        code_str = str(raw_code).strip() if raw_code is not None else None
        row[1] = code_dict.get(code_str, "NULL")
        cursor.updateRow(row)

arcpy.AddMessage("Functional_Class field populated successfully.")
