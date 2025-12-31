# -*- coding: utf-8 -*-
import arcpy
from collections import defaultdict

arcpy.env.overwriteOutput = True

# -----------------------------
# Parameters
# -----------------------------
input_points = arcpy.GetParameterAsText(0)     # Input points
roads_fc = arcpy.GetParameterAsText(1)         # Road centerlines
road_name_field = arcpy.GetParameterAsText(2) # Road name field
MAX_DIST_FT = 250

# -----------------------------
# Add output field
# -----------------------------
if "nearest_intersection" not in [f.name for f in arcpy.ListFields(input_points)]:
    arcpy.management.AddField(input_points, "nearest_intersection", "TEXT", field_length=150)

# -----------------------------
# Create TRUE intersection points
# -----------------------------
arcpy.AddMessage("Creating true road intersections...")
intersections_fc = "in_memory\\intersections"
arcpy.analysis.Intersect([roads_fc], intersections_fc, "ALL", "", "POINT")

# -----------------------------
# Spatial join roads → intersections
# (this is the critical step)
# -----------------------------
arcpy.AddMessage("Joining road names to intersections...")
join_fc = "in_memory\\intersection_roads"
arcpy.analysis.SpatialJoin(
    intersections_fc,
    roads_fc,
    join_fc,
    "JOIN_ONE_TO_MANY",
    "KEEP_ALL",
    match_option="INTERSECT"
)

# -----------------------------
# Build intersection → road-name list
# Group by geometry (XY), not OID
# -----------------------------
intersection_names = defaultdict(set)

with arcpy.da.SearchCursor(join_fc, ["SHAPE@XY", road_name_field]) as cursor:
    for xy, road in cursor:
        if road:
            intersection_names[xy].add(road)

# Convert to "Street 1 & Street 2"
intersection_label = {}
for xy, roads in intersection_names.items():
    if len(roads) >= 2:
        names = sorted(list(roads))
        intersection_label[xy] = f"{names[0]} & {names[1]}"
    else:
        intersection_label[xy] = None  # single road = NOT an intersection

# -----------------------------
# Near analysis (distance-limited)
# -----------------------------
arcpy.AddMessage("Finding points near intersections...")
arcpy.analysis.Near(
    input_points,
    intersections_fc,
    f"{MAX_DIST_FT} Feet",
    "NO_LOCATION",
    "NO_ANGLE"
)

# Build lookup for NEAR_FID → XY
intersection_xy = {}
with arcpy.da.SearchCursor(intersections_fc, ["OID@", "SHAPE@XY"]) as cursor:
    for oid, xy in cursor:
        intersection_xy[oid] = xy

# -----------------------------
# Populate output field
# -----------------------------
arcpy.AddMessage("Populating nearest_intersection field...")
with arcpy.da.UpdateCursor(input_points, ["NEAR_FID", "nearest_intersection"]) as cursor:
    for near_fid, _ in cursor:
        if near_fid == -1 or near_fid not in intersection_xy:
            value = "Not at an intersection / Unknown intersection"
        else:
            xy = intersection_xy[near_fid]
            value = intersection_label.get(xy)

            if not value:
                value = "Not at an intersection / Unknown intersection"

        cursor.updateRow([near_fid, value])

arcpy.AddMessage("Done. Intersections correctly labeled.")
