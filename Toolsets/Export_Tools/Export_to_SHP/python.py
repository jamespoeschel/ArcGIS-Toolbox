import arcpy
import os

# --- USER INPUT ---
feature = arcpy.GetParameterAsText(0)  # Feature class or layer to export

# --- PROJECT HOME FOLDER ---
aprx = arcpy.mp.ArcGISProject("CURRENT")
project_home_folder = aprx.homeFolder  # Get the project home folder

# --- CHECK IF 'DATA' FOLDER EXISTS ---
data_folder_path = os.path.join(project_home_folder, "DATA")

# If the 'DATA' folder exists, use that for the new folder
if os.path.exists(data_folder_path):
    new_folder_path = os.path.join(data_folder_path, f"{os.path.basename(feature)}_shp")
else:
    # If 'DATA' folder doesn't exist, use the project home folder itself
    new_folder_path = os.path.join(project_home_folder, f"{os.path.basename(feature)}_shp")

# Create the folder if it doesn't already exist
if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)

# --- OUTPUT SHAPEFILE PATH ---
output_shapefile = os.path.join(new_folder_path, f"{os.path.basename(feature)}.shp")

# --- EXPORT TO SHAPEFILE ---
try:
    arcpy.AddMessage(f"Exporting {feature} to {output_shapefile}...")

    # Export the feature class or layer to a shapefile
    arcpy.conversion.FeatureClassToShapefile(
        feature,  # Positional argument, not 'in_features'
        new_folder_path
    )

    arcpy.AddMessage(f"✅ Export successful! Shapefile saved to: {output_shapefile}")

except Exception as e:
    arcpy.AddError(f"❌ Failed to export shapefile. Error: {str(e)}")
    raise
