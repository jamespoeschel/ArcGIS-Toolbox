import os

# Get input parameter
crashLayer = arcpy.GetParameterAsText(0)

# Ped fields
pedFields = ["Pedestrian", "Other Pedestrian (person in a building, skater, personal conveyance, etc.)", 
            "Other Conveyance", "Scooter (non-Electric)", "Wheelchair (non-electric)", "Wheelchair (electric)", 
            "Occupant Of a Non-Motor Vehicle Transportation Device"] 
### Conveyance means a means of transportation, which could include skateboards, rollerblades, and non-electric scooters which are considered pedestrians
### People in wheelchairs whether electric or non-electric are legally considered pedestrians

# Bike fields
bikeFields = ["Bicyclist", "Other Pedalcyclist", "Pedalcyclist", 
             "Cyclist (non-electric)", "Cyclist (Electric)", 
             "Scooter (electric)"]
### Electric scooters are legally equivalent to bicyclists

# Fields and Severity mapping
reportTypeField = "Detailed_Report_Type"
nonMotoristField = "NonMotoristType"
newCrashDetailField = "AutoPedBike_SeverityDetail"

severityDict = {
    "Fatal": "K", 
    "Severe Injury": "SI", 
    "Minor Injury": "MI", 
    "Possible Injury": "PI", 
    "Property Damage Only": "PDO"
}

# Add new field if it doesn't exist
if newCrashDetailField not in [f.name for f in arcpy.ListFields(crashLayer)]:
    arcpy.AddField_management(crashLayer, newCrashDetailField, "TEXT", field_length=10)
    
    
# Calculate the new field
with arcpy.da.UpdateCursor(crashLayer, [reportTypeField, nonMotoristField, newCrashDetailField]) as cursor:
    for row in cursor:
        severity = row[0]
        nonMotorist = row[1]
        severityCode = severityDict.get(severity, "Unknown")

        # Determine the crash type and severity detail
        if nonMotorist in pedFields:
            row[2] = f"{severityCode} Ped"
        elif nonMotorist in bikeFields:
            row[2] = f"{severityCode} Bike"
        else:
            row[2] = severityCode
        
        cursor.updateRow(row)

arcpy.AddMessage("AutoPedBike_SeverityDetail field calculated successfully.")
