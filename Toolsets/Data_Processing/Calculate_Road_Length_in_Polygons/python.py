
import arcpy

# Parameters
roads_layer = arcpy.GetParameterAsText(0)       # Roads layer (feature layer)
polygons_layer = arcpy.GetParameterAsText(1)    # Polygon layer (feature layer)
polygon_field = arcpy.GetParameterAsText(2)     # Field in polygons to store the sum of lengths
length_field = arcpy.GetParameterAsText(3)      # Length field in roads layer

# Enable editing for the polygon layer
with arcpy.da.UpdateCursor(polygons_layer, ['SHAPE@', polygon_field]) as polygon_cursor:
    for polygon in polygon_cursor:
        polygon_geom = polygon[0]

        # Select roads that have their center within the current polygon
        arcpy.management.SelectLayerByLocation(
            roads_layer, 
            "HAVE_THEIR_CENTER_IN", 
            polygon_geom
        )

        # Sum up the length values of the selected roads
        total_length = 0
        with arcpy.da.SearchCursor(roads_layer, [length_field]) as roads_cursor:
            for road in roads_cursor:
                total_length += road[0]

        # Update the polygon field with the total length
        polygon[1] = total_length
        polygon_cursor.updateRow(polygon)

# Clear selection
arcpy.management.SelectLayerByAttribute(roads_layer, "CLEAR_SELECTION")
arcpy.management.SelectLayerByAttribute(polygons_layer, "CLEAR_SELECTION")
