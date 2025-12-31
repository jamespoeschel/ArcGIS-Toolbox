import arcpy

# Get input parameters from script tool
layer_names = arcpy.GetParameterAsText(0)  # Multiple layer names (semicolon-separated)
where_clause = arcpy.GetParameterAsText(1)  # Custom WHERE clause

# Access the current ArcGIS Pro project
aprx = arcpy.mp.ArcGISProject("CURRENT")

# Get the first map (modify if needed)
map_obj = aprx.activeMap

# Convert input string to a list of layer names
layer_list = layer_names.split(";")

# Apply definition query to each layer
for layer_name in layer_list:
    layer_name = layer_name.strip()
    layer = None
    
    # Find the layer in the map
    for lyr in map_obj.listLayers():
        arcpy.AddMessage(f"Found layer in map: {lyr.name}")
        if lyr.name == layer_name:
            layer = lyr
            break

    if layer is None:
        arcpy.AddWarning(f"Layer '{layer_name}' not found in the project. Skipping...")
        continue

    try:
        arcpy.AddMessage(f"Applying definition query to: {layer_name} ...")
        layer.definitionQuery = where_clause
        arcpy.AddMessage(f"Definition query applied: {where_clause}")
    except Exception as e:
        arcpy.AddError(f"Error processing {layer_name}: {str(e)}")

arcpy.AddMessage("Definition query applied successfully!")
