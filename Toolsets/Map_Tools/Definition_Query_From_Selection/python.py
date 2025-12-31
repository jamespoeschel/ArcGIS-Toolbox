import arcpy

featureInput = arcpy.GetParameterAsText(0)

def qdef_selected_features(lyr):
    desc = arcpy.Describe(lyr)
    
    # Get the OID field name
    oid_field_name = desc.OIDFieldName
    arcpy.AddMessage(f"OID Field Name: {oid_field_name}")
    
    # Get a semicolon-delimited string of selected feature IDs 
    fid_list = desc.FIDSet.split(";")
    
    # Check if fid_list is empty
    if not fid_list or fid_list == ['']:
        arcpy.AddError("No features are selected in the layer.")
        return
    
    # Build the query definition
    query = '{} IN ({})'.format(oid_field_name, ",".join(fid_list))
    arcpy.AddMessage(f"Definition Query: {query}")
    
    # apply the query definition back to the layer   
    lyr.definitionQuery = query

try:
    # Access the current project and active map
    aprx = arcpy.mp.ArcGISProject('current')
    m = aprx.activeMap
    
    # Get the list of layers matching the input name
    layers = m.listLayers(featureInput)
    
    # Check if the layer exists
    if not layers:
        arcpy.AddError(f"No layers found with the name '{featureInput}', please make sure the layer is not in a group")
    else:
        # Proceed with the first matching layer
        lyr = layers[0]
        qdef_selected_features(lyr)

except Exception as e:
    arcpy.AddError(f"An error occurred: {e}")
