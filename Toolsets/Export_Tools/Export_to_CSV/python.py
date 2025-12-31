import arcpy
import os

# Get input table parameter
inputTable = arcpy.GetParameterAsText(0)

# Get the project home folder
homeFolder = arcpy.mp.ArcGISProject("CURRENT").homeFolder

# Create the output CSV file name
outputCSV = os.path.join(homeFolder, f"{os.path.basename(inputTable)}.csv")

# Export the table to CSV
arcpy.conversion.TableToTable(inputTable, homeFolder, os.path.basename(outputCSV))

# Construct the .csv.xml file path
outputCSVXML = f"{outputCSV}.xml"

# Delete the .csv.xml file if it exists
if os.path.exists(outputCSVXML):
    os.remove(outputCSVXML)

# Add message showing where the CSV was saved
arcpy.AddMessage(f"Table successfully exported to: {outputCSV}")
