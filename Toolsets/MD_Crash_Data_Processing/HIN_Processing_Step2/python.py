# Import modules
import arcpy

# Set environments
current_project = arcpy.mp.ArcGISProject("CURRENT")  # Get current project
arcpy.env.workspace = current_project.defaultGeodatabase
arcpy.env.overwriteOutput = True

# Set parameters
CrashData = arcpy.GetParameterAsText(0)
CrashField = arcpy.GetParameterAsText(1)
HIN = arcpy.GetParameterAsText(2)
Distance_Value = arcpy.GetParameterAsText(3)

# Add necessary fields (including renamed and new fields)
arcpy.management.AddField(HIN, "ID_Number", "LONG", "", "", "", "ID")
arcpy.management.AddField(HIN, "RoadName", "Text", "", "", "", "Road Name")
arcpy.management.AddField(HIN, "RoadExtent", "Text", "", "", "", "Road Extent")
arcpy.management.AddField(HIN, "K", "LONG", "", "", "", "Fatal Crashes")
arcpy.management.AddField(HIN, "SI", "LONG", "", "", "", "Severe Injury Crashes")
arcpy.management.AddField(HIN, "AllInjuries", "LONG", "", "", "", "Poss Minor Severe Injury Crashes")
arcpy.management.AddField(HIN, "KSI", "LONG", "", "", "", "KSI Total")
arcpy.management.AddField(HIN, "Ped", "LONG", "", "", "", "Pedestrian Related")
arcpy.management.AddField(HIN, "Bike", "LONG", "", "", "", "Bicycle Related")
arcpy.management.AddField(HIN, "AllPedBike", "LONG", "", "", "", "All Ped Bike Total")
arcpy.management.AddField(HIN, "K_PedBike", "LONG", "", "", "", "Fatal Ped Bike Total")
arcpy.management.AddField(HIN, "SI_PedBike", "LONG", "", "", "", "Severe Ped Bike Total")
arcpy.management.AddField(HIN, "KSIPB", "LONG", "", "", "", "KSI Ped Bike Total")
arcpy.management.AddField(HIN, "Length_Miles", "DOUBLE", "", "", "", "Length in Miles")
arcpy.management.AddField(HIN, "KSIPBpMile", "DOUBLE", "", "", "", "KSI Ped Bike p Mile")
arcpy.management.AddField(HIN, "SpeedLimit", "Text", "", "", "", "Speed Limit")
arcpy.management.AddField(HIN, "NumTravelLanes", "Text", "", "", "", "Number of Travel Lanes")

# Get the total length of each road
arcpy.management.CalculateGeometryAttributes(HIN, [["Length_Miles", "LENGTH_GEODESIC"]], length_unit="MILES_US")

# Dictionary for crash type grouping (updated with new types)
crash_type_dict = {
    "K": ["K", "K Ped", "K Bike"],
    "SI": ["SI", "SI Ped", "SI Bike"],
    "Ped": ["PDO Ped", "K Ped", "SI Ped", "MI Ped", "PI Ped"],
    "Bike": ["PDO Bike", "K Bike", "SI Bike", "MI Bike", "PI Bike"],
    "AllInjuries": ["MI", "MI Ped", "MI Bike", "PI", "PI Ped", "PI Bike", "SI", "SI Ped", "SI Bike"],
    "KSI": ["K", "K Ped", "K Bike", "SI", "SI Ped", "SI Bike"],
    "AllPedBike": ["PDO Ped", "K Ped", "SI Ped", "MI Ped", "PI Ped", "PDO Bike", "K Bike", "SI Bike", "MI Bike", "PI Bike"],
    "K_PedBike": ["K Ped", "K Bike"],
    "SI_PedBike": ["SI Ped", "SI Bike"],
    "KSIPB": ["K", "K Ped", "K Bike", "SI", "SI Ped", "SI Bike", "PDO Ped", "MI Ped", "PI Ped", "PDO Bike", "MI Bike", "PI Bike"]
}

# Iterate over each HIN road segment (including new fields)
with arcpy.da.UpdateCursor(HIN, ["SHAPE@", "K", "SI", "Ped", "Bike", "AllInjuries", "KSI", "AllPedBike", "K_PedBike", "SI_PedBike", "KSIPB", "Length_Miles", "KSIPBpMile"]) as cursor:
    for row in cursor:
        road_geom = row[0]

        # Select crashes within the distance from this HIN road segment
        arcpy.SelectLayerByLocation_management(CrashData, "WITHIN_A_DISTANCE", road_geom, Distance_Value)

        # Count crashes for each type (including new types)
        counts = {
            "K": 0, "SI": 0, "Ped": 0, "Bike": 0, 
            "AllInjuries": 0, "KSI": 0, "AllPedBike": 0, 
            "K_PedBike": 0, "SI_PedBike": 0, "KSIPB": 0
        }
        with arcpy.da.SearchCursor(CrashData, CrashField) as crash_cursor:
            for crash_row in crash_cursor:
                crash_type = crash_row[0]

                # Assign crash to relevant category
                for crash_category, types in crash_type_dict.items():
                    if crash_type in types:
                        counts[crash_category] += 1

        # Update the row with the counts (new fields included)
        row[1] = counts["K"]
        row[2] = counts["SI"]
        row[3] = counts["Ped"]
        row[4] = counts["Bike"]
        row[5] = counts["AllInjuries"]
        row[6] = counts["KSI"]
        row[7] = counts["AllPedBike"]
        row[8] = counts["K_PedBike"]
        row[9] = counts["SI_PedBike"]
        row[10] = counts["KSIPB"]

        # Calculate KSIPBpMile (if Length_Miles > 0 to avoid division by zero)
        length_miles = row[11]
        if length_miles > 0:
            row[12] = counts["KSIPB"] / length_miles
        else:
            row[12] = 0  # Set to 0 if the length is 0

        # Update the row in the cursor
        cursor.updateRow(row)

# Clear selections
arcpy.SelectLayerByAttribute_management(CrashData, "CLEAR_SELECTION")
