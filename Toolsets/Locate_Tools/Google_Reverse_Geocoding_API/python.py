# -*- coding: utf-8 -*-
import arcpy
import requests

arcpy.env.overwriteOutput = True

# -------------------------------------------------------------------------
# Script parameters
# -------------------------------------------------------------------------
inFeature = arcpy.GetParameterAsText(0)       # Input Feature Layer
Long_Field = arcpy.GetParameterAsText(1)     # Longitude field name
Lat_Field = arcpy.GetParameterAsText(2)      # Latitude field name

# Your Google API key
API_KEY = 'YOUR AKI KEY HERE'  

# -------------------------------------------------------------------------
# Check feature count
# -------------------------------------------------------------------------
result = arcpy.GetCount_management(inFeature)
num_rows = int(result.getOutput(0))
arcpy.AddMessage(f"Number of features in layer: {num_rows}")

if num_rows > 1000:
    arcpy.AddError(
        "Feature layer has more than 1,000 rows. "
        "Please use a smaller dataset. Google will charge us money for 40,000 rows per month"
    )
    raise ValueError("Too many rows")

# -------------------------------------------------------------------------
# Reverse Geocoding Function
# -------------------------------------------------------------------------
def reverse_geocode(lat, lng):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    params = {
        "latlng": f"{lat},{lng}",
        "key": API_KEY
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    status = data.get("status", "UNKNOWN")
    arcpy.AddMessage(f"Reverse geocode status: {status}")

    if status == "OK":
        result = data["results"][0]
        formatted_address = result.get("formatted_address", "NA")
        location_type = result["geometry"].get("location_type", "NA")
        place_id = result.get("place_id", "NA")
        return formatted_address, location_type, place_id
    elif status == "ZERO_RESULTS":
        return "NA", "NA", "NA"
    else:
        return "ERROR", status, "NA"

# -------------------------------------------------------------------------
# Add output fields if they don't exist
# -------------------------------------------------------------------------
for field_name in ["formatted_address", "location_type", "place_id"]:
    if field_name not in [f.name for f in arcpy.ListFields(inFeature)]:
        arcpy.AddMessage(f"Adding field: {field_name}")
        arcpy.AddField_management(inFeature, field_name, "TEXT", field_length=255)

# -------------------------------------------------------------------------
# Process each feature
# -------------------------------------------------------------------------
fields = [Lat_Field, Long_Field, "formatted_address", "location_type", "place_id"]

with arcpy.da.UpdateCursor(inFeature, fields) as cursor:
    for idx, row in enumerate(cursor):
        lat = row[0]
        lng = row[1]

        if lat is not None and lng is not None:
            arcpy.AddMessage(f"Processing feature {idx + 1} ...")
            addr, loc_type, pid = reverse_geocode(lat, lng)
            row[2] = addr
            row[3] = loc_type
            row[4] = pid
        else:
            row[2] = "NA"
            row[3] = "NA"
            row[4] = "NA"

        cursor.updateRow(row)

arcpy.AddMessage("Reverse geocoding complete!")
