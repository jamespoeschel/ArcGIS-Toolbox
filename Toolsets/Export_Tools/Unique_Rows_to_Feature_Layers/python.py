# Created: 06/22/2024

import arcpy
import re

# Get parameters
FeatureLayer1 = arcpy.GetParameterAsText(0)
UniqueField = arcpy.GetParameterAsText(1)

# Set workspace and environment settings
aprx = arcpy.mp.ArcGISProject("CURRENT")
arcpy.env.overwriteOutput = True
arcpy.env.addOutputsToMap = True

def sanitize_feature_class_name(name):
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove special characters
    name = re.sub(r'\W+', '', name)
    return name

try:
    # Get the first map in the current project
    map_doc = aprx.listMaps()[0]  # Automatically selects the first map
    
    # List to hold the output layers
    output_layers = []

    # Create a search cursor and loop through the selected records
    with arcpy.da.SearchCursor(FeatureLayer1, [UniqueField], "", "", "", ("DISTINCT", UniqueField)) as cursor:
    ##with arcpy.da.SearchCursor(FeatureLayer1, [UniqueField]) as cursor:  #for when you want all rows
        for i, row in enumerate(cursor):
            UniqueString = row[0]
            sanitized_name = sanitize_feature_class_name(str(UniqueString))
            whereClause = "{} = '{}'".format(arcpy.AddFieldDelimiters(FeatureLayer1, UniqueField), UniqueString)
            
            # Create a unique temporary layer name
            tempLayerName = "tempLayer_" + sanitized_name
            
            try:
                # Make a feature layer of just the current selection
                arcpy.MakeFeatureLayer_management(FeatureLayer1, tempLayerName, whereClause)
                arcpy.AddMessage("Processing {0}.".format(UniqueString))
                
                # Add the feature layer to the map with a meaningful name
                result = arcpy.management.MakeFeatureLayer(tempLayerName)
                layer = result.getOutput(0)
                map_doc.addLayer(layer)
                
                # Set the name of the added layer
                added_layer = map_doc.listLayers(layer.name)[0]
                added_layer.name = sanitized_name
                
                output_layers.append(added_layer)
                arcpy.AddMessage("Created and added feature layer: {0}".format(sanitized_name))
                arcpy.AddMessage(f"Layer added to map: {map_doc.name}")

                
                # Exit loop after processing the last row
                #if i == cursor.rowcount - 1:
                #    break
                
            except Exception as e:
                arcpy.AddError("Could not create feature layer for {0}. Error: {1}".format(UniqueString, e))
except Exception as e:
    arcpy.AddError("There was a problem performing the spatial selection or creating the feature layer. Error: {0}".format(e))
finally:
    # Clean up cursor
    del row, cursor

# Set the output parameter for the feature layers
arcpy.SetParameterAsText(2, ";".join([layer.name for layer in output_layers]))
