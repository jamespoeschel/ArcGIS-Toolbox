import arcpy
import os

# Get parameters from the tool
crashData = arcpy.GetParameterAsText(0)
hinData = arcpy.GetParameterAsText(1)
idField = arcpy.GetParameterAsText(2)

# Get the project home folder for saving outputs
homeFolder = arcpy.mp.ArcGISProject("CURRENT").homeFolder

# Set the search distance
searchDistance = "150 Feet"

# Loop through each row in the HIN layer
with arcpy.da.SearchCursor(hinData, ["SHAPE@", idField]) as cursor:
    for row in cursor:
        geom = row[0]  # Get geometry of the current HIN feature
        feature_id = row[1]  # Get the value from the ID field
        
        # Select crashes that intersect within 150 feet of the current HIN feature
        arcpy.MakeFeatureLayer_management(crashData, "crash_layer")
        arcpy.SelectLayerByLocation_management("crash_layer", "INTERSECT", geom, searchDistance)

        # Check if any features were selected
        selected_count = int(arcpy.GetCount_management("crash_layer").getOutput(0))
        
        if selected_count > 0:
            # Export selected crashes to CSV with "HIN_ID_" prefix
            output_csv = os.path.join(homeFolder, f"HIN_ID_{feature_id}_crashes.csv")
            arcpy.TableToTable_conversion("crash_layer", homeFolder, f"HIN_ID_{feature_id}_crashes.csv")
            arcpy.AddMessage(f"Exported {selected_count} crashes to {output_csv}")

            # Delete the .xml file that gets created
            xml_file = output_csv.replace(".csv", ".csv.xml")
            if os.path.exists(xml_file):
                os.remove(xml_file)
                arcpy.AddMessage(f"Deleted metadata file: {xml_file}")
        else:
            arcpy.AddMessage(f"No crashes found within 150 feet of HIN feature ID: {feature_id}")
        
        # Clear selection
        arcpy.SelectLayerByAttribute_management("crash_layer", "CLEAR_SELECTION")
