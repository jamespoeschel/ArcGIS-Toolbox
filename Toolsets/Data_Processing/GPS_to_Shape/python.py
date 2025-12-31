# Import modules
import arcpy
import csv

# Set variables and paths
arcpy.env.workspace = arcpy.GetParameterAsText(0)
carGPS = arcpy.GetParameterAsText(1)
timeField = arcpy.GetParameterAsText(2)
uniqueField = arcpy.GetParameterAsText(3)
latField = arcpy.GetParameterAsText(4)
longField = arcpy.GetParameterAsText(5)
shapeType = arcpy.GetParameterAsText(6)
outPath = arcpy.env.workspace
fcOutput = outPath + r"\gpsPath"
featureClass = "gpsPath"
polygonfeatureClass = "gpsShape"
LapField = "Unique_Field"  # Field to add in feature class
arcpy.env.overwriteOutput = True
arcpy.addOutputsToMap = True


if shapeType == "POLYLINE":
    # Open csv document
    with open(carGPS) as GPStable:
        # Read the header line and get important field indices
        csvReader = csv.reader(GPStable)
        header = next(csvReader)
        lapIndex = header.index(uniqueField)
        longitudeIndex = header.index(longField)
        latitudeIndex = header.index(latField)
        timeField = header.index(timeField)

        # Create empty dictionary. Keys = Lap, Value = Coords
        lapDictionary = {}

        # Start a loop to create coordinates
        for row in csvReader:
            if '#' not in row[timeField]:   # Loops applies when there is no lap finish time stamp in timeField

                # Create variables for all items of interest
                lap = int(row[lapIndex])
                longitude = float(row[longitudeIndex])
                latitude = float(row[latitudeIndex])
                coords = (longitude, latitude)

                # Add the lap into the dictionary key if not already in it
                if lap not in lapDictionary:
                    lapDictionary[lap] = []

                # Append coords to list to the cooresponding lap
                lapDictionary[lap].append(coords)

        # Set spatial reference for WGS 1984 WKID number
        sr = arcpy.SpatialReference(4326)

        # Create Polyline Feature Class
        arcpy.management.CreateFeatureclass(outPath, featureClass, "POLYLINE", "", "", "", sr)

        # Add Field for the Number of Laps
        arcpy.management.AddField(featureClass, LapField, "SHORT", 4)

        # Initiate Insert Cursor with Shape token and LapField
        with arcpy.da.InsertCursor(featureClass, ("SHAPE@", LapField)) as cursor:
            # Insert polylines and update Lap_Number field
            for lap, coords_list in lapDictionary.items():
                array = arcpy.Array([arcpy.Point(*coords) for coords in coords_list]) # Create an array of points with coords broken into x,y 's
                polyline = arcpy.Polyline(array, sr)
                cursor.insertRow((polyline, lap))

        # Initiate Update Cursor to add lap in the LapField using a counter
        with arcpy.da.UpdateCursor(featureClass, [LapField]) as lapCursor:
            counter = 0
            for row in lapCursor:
                row[0] = counter
                lapCursor.updateRow(row)
                counter += 1

else:
    # Open csv document
    with open(carGPS) as GPStable:
        # Read the header line and get important field indices
        csvReader = csv.reader(GPStable)
        header = next(csvReader)
        lapIndex = header.index(uniqueField)
        longitudeIndex = header.index(longField)
        latitudeIndex = header.index(latField)
        timeField = header.index(timeField)

        # Create empty dictionary. Keys = Lap, Value = Coords
        lapDictionary = {}

        # Start a loop to create coordinates
        for row in csvReader:
            if '#' not in row[timeField]:   # Loops applies when there is no lap finish time stamp in timeField

                # Create variables for all items of interest
                lap = int(row[lapIndex])
                longitude = float(row[longitudeIndex])
                latitude = float(row[latitudeIndex])
                coords = (longitude, latitude)

                # Add the lap into the dictionary key if not already in it
                if lap not in lapDictionary:
                    lapDictionary[lap] = []

                # Append coords to list to the cooresponding lap
                lapDictionary[lap].append(coords)

        # Set spatial reference for WGS 1984 WKID number
        sr = arcpy.SpatialReference(4326)

        # Create Polyline Feature Class
        arcpy.management.CreateFeatureclass(outPath, polygonfeatureClass, "POLYGON", "", "", "", sr)

        # Add Field for the Number of Laps
        arcpy.management.AddField(polygonfeatureClass, LapField, "SHORT", 4)

        # Initiate Insert Cursor with Shape token and LapField
        with arcpy.da.InsertCursor(polygonfeatureClass, ("SHAPE@", LapField)) as cursor:
            # Insert polylines and update Lap_Number field
            for lap, coords_list in lapDictionary.items():
                array = arcpy.Array([arcpy.Point(*coords) for coords in coords_list]) # Create an array of points with coords broken into x,y 's
                polygon = arcpy.Polygon(array, sr)
                cursor.insertRow((polygon, lap))

        # Initiate Update Cursor to add lap in the LapField using a counter
        with arcpy.da.UpdateCursor(polygonfeatureClass, [LapField]) as lapCursor:
            counter = 0
            for row in lapCursor:
                row[0] = counter
                lapCursor.updateRow(row)
                counter += 1
