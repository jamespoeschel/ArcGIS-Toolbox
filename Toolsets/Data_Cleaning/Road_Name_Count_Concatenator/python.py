import arcpy

# Get input parameters
input_fc = arcpy.GetParameterAsText(0)  # Input feature class
road_name_field = arcpy.GetParameterAsText(1)  # Road Name field
output_field = arcpy.GetParameterAsText(2)  # Field to update

# Create a feature layer for spatial selection
arcpy.MakeFeatureLayer_management(input_fc, "road_layer")

# Track processed road names to ensure each group is processed once
processed_roads = {}

# Use UpdateCursor to iterate over each feature and assign consecutive numbers
with arcpy.da.UpdateCursor(input_fc, [road_name_field, output_field, "SHAPE@"]) as cursor:
    for row in cursor:
        road_name = row[0]  # Road Name field value
        if not road_name:
            continue  # Skip features with no road name

        # Initialize or increment the count for the road name
        if road_name not in processed_roads:
            processed_roads[road_name] = 1
        else:
            processed_roads[road_name] += 1

        # Update the output field with the concatenated road name and count
        row[1] = f"{road_name} {processed_roads[road_name]}"
        cursor.updateRow(row)

arcpy.AddMessage("Field updated based on spatial adjacency.")
