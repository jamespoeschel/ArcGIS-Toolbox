import arcpy

# Script tool parameters
in_layer = arcpy.GetParameterAsText(0)
input_field = arcpy.GetParameterAsText(1)
desired_type = arcpy.GetParameterAsText(2)  # e.g., "TEXT", "SHORT", etc.
run_calculation = arcpy.GetParameter(3)     # Boolean (True/False), not GetParameterAsText

# Construct new field name
new_field = f"{input_field}_{desired_type}"

# Add the new field
arcpy.AddMessage(f"Adding field '{new_field}' of type {desired_type}")
arcpy.AddField_management(in_layer, new_field, desired_type)

# Conditionally copy data from original field
if run_calculation:
    expression = f'!{input_field}!'
    arcpy.AddMessage(f"Calculating field '{new_field}' from '{input_field}'")
    arcpy.CalculateField_management(in_layer, new_field, expression, "PYTHON3")
    arcpy.AddMessage("Field added and values copied successfully.")
else:
    arcpy.AddMessage("Field added, but skipping value copy as requested, do manually for larger datasets to save time.")
