# -*- coding: utf-8 -*-
import arcpy

# Script parameters
input_layer = arcpy.GetParameterAsText(0)  # Input feature layer

# Define field names
lon_field = "Longitude"
lat_field = "Latitude"

# Add Longitude and Latitude fields if they don’t exist
existing_fields = [f.name for f in arcpy.ListFields(input_layer)]

if lon_field not in existing_fields:
    arcpy.AddField_management(input_layer, lon_field, "DOUBLE")

if lat_field not in existing_fields:
    arcpy.AddField_management(input_layer, lat_field, "DOUBLE")

# Calculate X and Y (Longitude and Latitude)
arcpy.management.CalculateGeometryAttributes(
    input_layer,
    [[lon_field, "POINT_X"], [lat_field, "POINT_Y"]],
    coordinate_system=arcpy.SpatialReference(4326)
)

arcpy.AddMessage("Longitude and Latitude fields added and calculated successfully.")
