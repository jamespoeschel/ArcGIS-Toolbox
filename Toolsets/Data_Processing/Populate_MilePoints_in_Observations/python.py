""" This code uses the Generate Points from Lines geoprocessing tool from ArcGIS PRO
    created by ESRI and adds to it to create miles points and add these mile point values to an observation layer.
    
    The Section 1 of the code takes the Generate Points from Lines tool and modifies it to remove or
    hard code certain parameters and makes the starting value offset by half of the user-inputted distance 
    
    Section 2 of the code continues from the generated points to
    split the road line at each offset point and populate the observations layer with the approximate mile point it is 
    located on.
"""

# Section 1

#import modules 

import arcpy
import os
from collections import namedtuple
import sys

# Set environments
current_project = arcpy.mp.ArcGISProject("CURRENT")  # Get current project
arcpy.env.workspace = current_project.defaultGeodatabase
workspace_path = current_project.defaultGeodatabase  # Get the default geodatabase of the current project to start an editting session later
arcpy.env.overwriteOutput = True

# Code below is copied from the Generate Points along Line tool and modified
point_placement = dict(DISTANCE=True, PERCENTAGE=False)

def create_points_from_lines(input_fc, output_fc, spatial_ref, percent=False,
                             dist=True, add_end_points=False, add_chainage=False):
    if percent:
        is_percentage = True
    else:
        is_percentage = False

    create_feature_class(input_fc, output_fc, spatial_ref)

    fid_name = 'ORIG_FID'
    len_name = 'ORIG_LEN'
    seq_name = 'ORIG_SEQ'

    # Add necessary fields
    if add_chainage:
        arcpy.management.AddFields(
            output_fc,
            [[fid_name, 'LONG'], [len_name, 'DOUBLE'], [seq_name, 'LONG']])
    else:
        arcpy.management.AddField(output_fc, fid_name, 'LONG')

    # Create new points based on input lines
    in_fields = ['SHAPE@', 'OID@']
    out_fields = ['SHAPE@', fid_name]
    if add_chainage:
        out_fields += [len_name, seq_name]

    out_fc_is_empty = True
    with arcpy.da.SearchCursor(input_fc, in_fields) as search_cursor:
        with arcpy.da.InsertCursor(output_fc, out_fields) as insert_cursor:
            for row in search_cursor:
                line = row[0]

                if line:  # if null geometry--skip
                    i = 1
                    if line.type == 'polygon':
                        line = line.boundary()

                    if add_end_points:
                        out_fc_is_empty = False
                        insert_values = [line.firstPoint, row[1]]
                        if add_chainage:
                            insert_values += [0, i]
                        insert_cursor.insertRow(insert_values)
                        i += 1

                    increment = (percent or dist)
                    cur_length = increment

                    if is_percentage:
                        max_position = 1.0
                    else:
                        max_position = line.length
                        
                    # Adjust starting length to distance / 2 to split lines between mile points
                    start_offset = dist / 2.0
                    cur_length = start_offset

                    while cur_length < max_position:
                        out_fc_is_empty = False
                        new_point = line.positionAlongLine(cur_length,
                                                           is_percentage)
                        insert_values = [new_point, row[1]]
                        if add_chainage:
                            if is_percentage:
                                insert_values += [line.queryPointAndDistance(new_point)[1], i]
                            else:
                                insert_values += [cur_length, i]
                        insert_cursor.insertRow(insert_values)
                        i += 1
                        cur_length += increment

                    if add_end_points:
                        end_point = line.positionAlongLine(1, True)
                        insert_values = [end_point, row[1]]
                        if add_chainage:
                            insert_values += [line.length, i]
                        insert_cursor.insertRow(insert_values)

        try:
            oid_name = get_OID_name(input_fc)
            arcpy.management.JoinField(out_fc, fid_name, input_fc, oid_name)
        except arcpy.ExecuteError:
            # In unlikely event that JoinField fails, proceed regardless,
            # as spatial and join field are already complete
            pass

    if out_fc_is_empty:
        arcpy.AddIDMessage('WARNING', 117)

    return


def create_feature_class(input_fc, output_fc, spatial_ref):

    desc = arcpy.Describe(input_fc)

    # Take flag environment over Describe property unless set to default
    support_m = arcpy.env.outputMFlag.upper() if arcpy.env.outputMFlag in ['Enabled', 'Disabled'] \
        else "ENABLED" if desc.hasM else "DISABLED"
    support_z = arcpy.env.outputZFlag.upper() if arcpy.env.outputZFlag in ['Enabled', 'Disabled'] \
        else "ENABLED" if desc.hasZ else "DISABLED"

    # Create output feature class
    arcpy.management.CreateFeatureclass(
        os.path.dirname(output_fc),
        os.path.basename(output_fc),
        geometry_type="POINT",
        has_m=support_m,
        has_z=support_z,
        spatial_reference=spatial_ref)

    return


def get_OID_name(in_data):

    d = arcpy.Describe(in_data)
    oid = getattr(d, 'OIDFieldName') \
          if hasattr(d, 'OIDFieldName') \
          else getattr(arcpy.Describe(d.catalogPath), 'OIDFieldName')
    return oid


def convert_units(dist, param_units, spatial_info):

    param_units = param_units.upper()

    if param_units in ['', None, 'UNKNOWN']:
        return dist
    else:
        if param_units != 'DECIMALDEGREES':
            p_conversion = arcpy.LinearUnitConversionFactor(param_units, 'meters')
        else:
            p_conversion = 111319.8

        try:
            sr_conversion = spatial_info.spatialReference.metersPerUnit
        except AttributeError:
            try:
                input_extent = spatial_info.extent

                centroid = input_extent.polygon.centroid
                point1 = centroid.Y, centroid.X - 0.5
                point2 = centroid.Y, centroid.X + 0.5
                sr_conversion = haversine(point1, point2) * 1000
            except Exception as err:
                # Fallback
                sr_conversion = 111319.8

        return dist * (p_conversion / sr_conversion)


def get_distance_and_units(dist):

    try:
        dist, units = dist.split(' ', 1)
    except ValueError:
        # ValueError occurs if units are not specified, use 'UNKNOWN'
        units = 'UNKNOWN'

    dist = dist.replace(',', '.')

    return float(dist), units


def haversine(point1, point2):

    from math import radians, sin, cos, asin, sqrt
    radius_of_earth_km = 6371
    lat1, lng1, lat2, lng2 = list(map(radians, list(point1 + point2)))
    d = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    return 2 * radius_of_earth_km * asin(sqrt(d))


if __name__ == '__main__':
    in_fc = arcpy.GetParameterAsText(0)
    obs_fc = arcpy.GetParameterAsText(1)
    out_fc = "Offset_MPs"  # Intermediate data that will be used to split the lines
    RoadName = arcpy.GetParameterAsText(3)
    distance = arcpy.GetParameterAsText(4)  # String
    chainage = False 

    describe = arcpy.Describe(in_fc)
    spatial_info = namedtuple('spatial_info', 'spatialReference extent')
    sp_info = spatial_info(spatialReference=describe.spatialReference,
                           extent=describe.extent)

    distanceNum = distance
    distance, param_linear_units = get_distance_and_units(distance)
    distance = convert_units(distance, param_linear_units,
                                 sp_info)
                                 
    incrementValue = float(distanceNum.split(' ')[0]) # Extract numeric part and convert to float
        
    create_points_from_lines(in_fc, out_fc, sp_info.spatialReference,
                                 dist=distance, add_end_points=False,
                                 add_chainage=chainage)

    try:
        arcpy.management.AddSpatialIndex(out_fc)
    except arcpy.ExecuteError:
        pass

# Add another MP fc that will be at the center of each split line
# Use the arcpy.management.GeneratePointsAlongLines since we do not have to modify the code
out_fc_MP = arcpy.GetParameterAsText(2)
arcpy.management.GeneratePointsAlongLines(in_fc, out_fc_MP, "DISTANCE", distance, "", "END_POINTS")




# Section 2

# Check that the spatial reference of the input features are the same and print
spatial_ref1 = arcpy.Describe(in_fc).spatialReference
spatial_ref2 = arcpy.Describe(obs_fc).spatialReference

if spatial_ref1.name == spatial_ref2.name:
    arcpy.AddMessage("Both the Observation Layer and the Road Layer are in the spatial reference: {}".format(spatial_ref1.name))
else:
    arcpy.AddWarning("The spatial references of the Observation Layer and the Road Layer are different.")
        
        

# Copy observations layer
copyObsLayer = "Snapped_Observations"
arcpy.management.CopyFeatures(obs_fc, copyObsLayer)
# Snap the observations layer to the closest road edge within 500'
arcpy.edit.Snap(copyObsLayer, [[in_fc, "EDGE", "500 Feet"]])

# Get the Total length of each road (not necessary but nice to have)
arcpy.management.AddField(in_fc, "Total_Length_Miles", "DOUBLE", "", "", "", "Length in Miles")
arcpy.management.CalculateGeometryAttributes(in_fc, [["Total_Length_Miles", "LENGTH_GEODESIC"]], length_unit="MILES_US"
)

# Add Mile Point fields in both MP layers to calculate later
arcpy.management.AddField(out_fc, "Mile_Point", "FLOAT", "", "", "", "Mile Point")
arcpy.management.AddField(out_fc_MP, "Mile_Point", "FLOAT", "", "", "", "Mile Point")




# Get unique road names
unique_road_names = set()
with arcpy.da.SearchCursor(out_fc, [RoadName]) as cursor:
    for row in cursor:
        unique_road_names.add(row[0])

# Iterate over each unique road name to populate Mile Points in the offset MPs
for road_name in unique_road_names:
    start_value = incrementValue/2  # Reset start value for each road name to half the distance increment
    
    query = f"{RoadName} = '{road_name}'"
            
    with arcpy.da.UpdateCursor(out_fc, ["Mile_Point"], query) as MP_Cursor:
        for row in MP_Cursor:
            row[0] = start_value  # Assign the current start_value to the field
            MP_Cursor.updateRow(row)
            start_value += incrementValue  # Increment the start_value for the next row
        
        

# Iterate over each unique road name to populate Mile Points in the normal MPs
for road_name in unique_road_names:
    start_value = 0.0  # Reset start value for each road name to half the distance increment
    
    query = f"{RoadName} = '{road_name}'"
            
    with arcpy.da.UpdateCursor(out_fc_MP, ["Mile_Point"], query) as MP_Cursor:
        for row in MP_Cursor:
            row[0] = start_value  # Assign the current start_value to the field
            MP_Cursor.updateRow(row)
            start_value += incrementValue  # Increment the start_value for the next row


# Check if the Advanced license is available and Split Lines using the offset MPs
roadCopy = "Road_Copy_SplitLines"
if arcpy.CheckProduct("ArcInfo") == "Available" or arcpy.CheckProduct("ArcInfo") == "AlreadyInitialized":
    arcpy.management.SplitLineAtPoint(in_fc, out_fc, roadCopy, "10 Feet")
else:
    msg = 'ArcGIS for Desktop Advanced license not available'
    print(msg)
    arcpy.AddMessage(msg)
    sys.exit(msg)

# Run a spatial join to get the MPs from the non-offset MPs to the split roads
roadCopy2 = "Road_Copy_Split_with_MPs"
arcpy.analysis.SpatialJoin(roadCopy, out_fc_MP, roadCopy2, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", "5 Feet")

# Run another spatial join to get the MP values from the split roads to the snapped observations layer
copyObsLayer2 = "Snapped_Obs_with_MPs"
arcpy.analysis.SpatialJoin(copyObsLayer, roadCopy2, copyObsLayer2, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", "5 Feet")


# Add a field to join the snapped observation layer to the original
joinField = "JoinID_Field"
arcpy.management.AddField(obs_fc, joinField, "LONG")
arcpy.management.AddField(copyObsLayer2, joinField, "LONG")

# Start an editting session and populate unique ID numbers in both observation layers 
seqStart = 0
seqIncrement = 1

with arcpy.da.Editor(workspace_path) as edit:
    with arcpy.da.UpdateCursor(obs_fc, [joinField]) as join_Cursor:
        for row in join_Cursor:
            row[0] = seqStart  # Assign the current start_value to the field
            join_Cursor.updateRow(row)
            seqStart += seqIncrement  # Increment the start_value for the next row

    seqStart = 0
    with arcpy.da.UpdateCursor(copyObsLayer2, [joinField]) as join_Cursor:
        for row in join_Cursor:
            row[0] = seqStart  # Assign the current start_value to the field
            join_Cursor.updateRow(row)
            seqStart += seqIncrement  # Increment the start_value for the next row

# Join the Mile_Points field from the snapped obs layer to the original obs layer
arcpy.management.JoinField(obs_fc, joinField, copyObsLayer2, joinField, "Mile_Point", "", "", "NEW_INDEXES")

# Add Completion Message
arcpy.AddMessage("Mile Points have successfully been added to the {} layer".format(obs_fc))

# Clean Up: Delete Intermediate Data
if arcpy.GetParameterAsText(5) == "true":
    arcpy.management.Delete(out_fc)
    arcpy.management.Delete(roadCopy)
    arcpy.management.Delete(roadCopy2)
    arcpy.management.Delete(copyObsLayer)
    arcpy.management.Delete(copyObsLayer2)
else:
    #Delete these layers regardless
    arcpy.management.Delete(roadCopy)  
    arcpy.management.Delete(copyObsLayer)
