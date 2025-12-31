import requests

# ArcGIS Pro parameter
place_name = arcpy.GetParameterAsText(0)


# ArcGIS Pro environment
arcpy.env.overwriteOutput = True

# Use the default project GDB
aprx = arcpy.mp.ArcGISProject("CURRENT")
default_gdb = aprx.defaultGeodatabase
output_fc = f"{default_gdb}\\OSM_POIs"

# Use Nominatim to get OSM ID and type
def get_osm_area_id(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': place,
        'format': 'json',
        'addressdetails': 1,
        'extratags': 1,
    }
    headers = {'User-Agent': 'ArcGISOverpassTool/1.0'}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if not data:
        raise ValueError("Place not found in Nominatim.")

    osm_type = data[0]['osm_type']
    osm_id = int(data[0]['osm_id'])

    # Area ID calculation per Overpass spec
    if osm_type == 'relation':
        area_id = 3600000000 + osm_id
    elif osm_type == 'node':
        area_id = 3600000000 + osm_id  # Less common, but supported
    else:
        raise ValueError("Unsupported OSM type.")
    
    return area_id

area_id = get_osm_area_id(place_name)

# List of tag combinations to fetch
# restaurants are commented out since they often result in too many points
tags = {
    'amenity': [
        'school', 'college', 'library', 'fire_station', 'hospital', 'clinic', 'place_of_worship',
        'community_centre', 'townhall', 'public_building',
        'restaurant', 'fast_food', 'cafe',
        'theatre' 
    ],
    'leisure': [
        'sports_centre', 'fitness_centre', 'club',
        'stadium' 
    ],
    'office': [
        'government', 'administrative', 'civil'
    ],
    'shop': [
        'supermarket', 'mall'
    ],
    'aeroway': [
        'aerodrome', 'airport'
    ]
}



# Build Overpass query
query_parts = []
for key, values in tags.items():
    for value in values:
        query_parts.append(f'node["{key}"="{value}"](area:{area_id});')
        query_parts.append(f'relation["{key}"="{value}"](area:{area_id});')

query = f"""
[out:json][timeout:25];
(
  {"".join(query_parts)}
);
out center;
"""

overpass_url = "http://overpass-api.de/api/interpreter"
response = requests.get(overpass_url, params={'data': query})
data = response.json()

# collect (name, type_value, lon, lat, geom_source)
poi_points = []
for element in data.get('elements', []):
    tags_in_element = element.get('tags', {})
    name = tags_in_element.get('name', 'Unnamed')

    poi_type = "Unknown"
    for key, values in tags.items():
        if key in tags_in_element and tags_in_element[key] in values:
            poi_type = tags_in_element[key]
            break
    
    # determine geometry source + coordinates
    if element['type'] == 'node':
        geom_source = 'point'
        lon = element.get('lon')
        lat = element.get('lat')
    elif element['type'] == 'way':
        geom_source = 'polygon'
        center = element.get('center')
        if center:
            lon = center.get('lon')
            lat = center.get('lat')
        else:
            continue  # skip if no center found
    else:
        continue  # skip relations for now

    poi_points.append((name, poi_type, lon, lat, geom_source))

if poi_points:
    # Create the feature class
    spatial_ref = arcpy.SpatialReference(4326)  # WGS84
    arcpy.management.CreateFeatureclass(
        out_path=default_gdb,
        out_name="OSM_POIs",
        geometry_type="POINT",
        spatial_reference=spatial_ref
    )
    arcpy.management.AddField(output_fc, "Name", "TEXT", field_length=255)
    arcpy.management.AddField(output_fc, "Type", "TEXT", field_length=255)
    arcpy.management.AddField(output_fc, "Geom_Source", "TEXT", field_length=50)

    with arcpy.da.InsertCursor(output_fc, ["SHAPE@XY", "Name", "Type", "Geom_Source"]) as cursor:
        for name, poi_type, lon, lat, geom_source in poi_points:
            cursor.insertRow([(lon, lat), name, poi_type, geom_source])

    # Add to map
    active_map = aprx.activeMap
    layer = active_map.addDataFromPath(output_fc)
    
    sym = layer.symbology
    sym.updateRenderer('UniqueValueRenderer')
    sym.renderer.fields = ['Type']
    layer.symbology = sym

    
    

    arcpy.AddMessage(f"Created feature class: {output_fc} with {len(poi_points)} POIs, and added to the map.")
else:
    arcpy.AddMessage("No POIs found for the given tags in {place_name}.")
