#Contributors: Lan Song, James Poeschel 

import arcpy
import requests
import pandas as pd
import os

arcpy.env.overwriteOutput = True

aprx = arcpy.mp.ArcGISProject("CURRENT")
inCSV = arcpy.GetParameterAsText(0)
FieldName = arcpy.GetParameterAsText(1)

API_KEY='YOUR AKI KEY HERE'

def getGeoCode(Location):
    params= {
        'key': API_KEY,
        'address': Location
    }
    base_url= 'https://maps.googleapis.com/maps/api/geocode/json?'
    response=requests.get(base_url,params=params)
    data = response.json()
    print(data['status'])
    if data['status'] == 'OK':
        result = data['results'][0]
        location=result['geometry']['location']
        formatted_address=result['formatted_address']
        location_Type=result['geometry']['location_type']
        return location['lat'],location['lng'],formatted_address,location_Type
    elif data['status'] == 'ZERO_RESULTS':
        return ('NA','NA','NA','NA')
    else:
        return('      ')
  
# Construct the output file path using the directory of the input CSV file
input_folder = os.path.dirname(inCSV)
outputFilePath = os.path.join(input_folder, f"{FieldName}_table.csv")  

#read the csv file
try:
    df = pd.read_csv(inCSV)
except Exception as e:
    arcpy.AddError(f"Error reading CSV file: {e}")
    raise

# Get the number of rows in the CSV file
num_rows = len(df)

# Print the number of rows
arcpy.AddMessage(f"Number of rows in the CSV file: {num_rows}")

# Check if the number of rows exceeds 40,000
if num_rows > 40000:
    arcpy.AddError("The CSV file contains more than 40,000 rows. Please provide a file with fewer rows.")
    raise ValueError("The CSV file contains more than 40,000 rows.")

for index, row in df.iterrows():
    address= row[f"{FieldName}"]         #Address field of user's table
    if address:
        print('it is processing'+ str(index))
        coord= getGeoCode(address)
        df.loc[index, 'lat']=coord[0]
        df.loc[index, 'lng']=coord[1]
        df.loc[index, 'formatted_address']=coord[2]
        df.loc[index, 'location_type']=coord[3]
       

df.to_csv(outputFilePath)

# Get the default project geodatabase path
default_gdb = aprx.defaultGeodatabase
output_feature_class = os.path.join(default_gdb, f"{FieldName}_points")

# Convert the CSV to a point feature class
arcpy.management.XYTableToPoint(outputFilePath, output_feature_class, "lng", "lat", "", arcpy.SpatialReference(4326))

# Add the new feature class to the current map
active_map = aprx.activeMap  # Get the currently active map
if active_map is not None:
    active_map.addDataFromPath(output_feature_class)
    arcpy.AddMessage(f"Feature class created and added to the active map: {output_feature_class}")
else:
    arcpy.AddWarning("No active map found. Feature class created but not added to any map.")
