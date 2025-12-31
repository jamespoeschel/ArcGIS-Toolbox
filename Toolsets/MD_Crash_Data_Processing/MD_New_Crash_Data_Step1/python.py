import pandas as pd
import arcpy
import os

# Get input parameters
occupants_csv = arcpy.GetParameterAsText(0)  # Path to the input CSV file
nonmotorist_csv = arcpy.GetParameterAsText(1)  # Path to the input CSV file
circumstance_csv = arcpy.GetParameterAsText(2)  # Path to the input CSV file
vehicle_csv = arcpy.GetParameterAsText(3)  # Path to the input CSV file
report_csv = arcpy.GetParameterAsText(4)  # Path to the input CSV file


# Get the project home folder
home_folder = arcpy.mp.ArcGISProject("CURRENT").homeFolder

# Create the output CSV file name
output_occupants_csv = os.path.join(home_folder, "CrashMap_OCCUPANTS_data_cleaned.csv")
output_nonmotorist_csv = os.path.join(home_folder, "CrashMap_NONMOTORIST_data_cleaned.csv")
output_circumstance_csv = os.path.join(home_folder, "CrashMap_CIRCUMSTANCES_data_cleaned.csv")
output_vehicle_csv = os.path.join(home_folder, "CrashMap_VEHICLE_data_cleaned.csv")
output_report_csv = os.path.join(home_folder, "CrashMap_REPORT_data_cleaned.csv")






### PART 1 - Occupants & NonMotorist Tables






# Define the hierarchy of DriverInjurySeverity
severity_hierarchy = [
    "Fatal Injury",
    "Suspected Serious Injury",
    "Suspected Minor Injury",
    "Possible Injury",
    "No Apparent Injury"
]

# Function to count severity types and add them as new fields
def count_severity(data, severity_field, prefix):
    # Create a pivot table to count occurrences of each severity type by 'Reportnumber'
    severity_counts = (
        data.groupby(["Reportnumber", severity_field])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=severity_hierarchy, fill_value=0)
    )

    # Rename columns with the appropriate prefix
    severity_counts.columns = [
        f"{prefix}_Fatalities",
        f"{prefix}_Severe_Injuries",
        f"{prefix}_Minor_Injuries",
        f"{prefix}_Possible_Injuries",
        f"{prefix}_PDO",
    ]
    
    # Reset the index so it can be merged back with the data
    severity_counts.reset_index(inplace=True)

    # Merge the counts back with the original data
    data = pd.merge(data, severity_counts, on="Reportnumber", how="left")

    return data

# Import the CSV files
occupants_data = pd.read_csv(occupants_csv)
nonmotorist_data = pd.read_csv(nonmotorist_csv)

# Field renaming map
rename_map = {
    "Type NM Description": "NonMotoristType",
    "ActionPriorToCrash NM Description": "NonMotoristMovement",
    "Gender NM": "NonMotoristSex",
    "Age NM": "NonMotoristAge",
    "InjuryStatus NM Description": "NonMotoristInjurySeverity"
}


# Rename fields if they exist
nonmotorist_data = nonmotorist_data.rename(columns={old_name: new_name for old_name, new_name in rename_map.items() if old_name in nonmotorist_data.columns})

# Ensure severity fields follow the defined hierarchy
occupants_data["InjuryStatus Occ Description"] = pd.Categorical(
    occupants_data["InjuryStatus Occ Description"], categories=severity_hierarchy, ordered=True
)

nonmotorist_data["NonMotoristInjurySeverity"] = pd.Categorical(
    nonmotorist_data["NonMotoristInjurySeverity"], categories=severity_hierarchy, ordered=True
)

# Count severity types and add fields for Occupants and Non-Motorist tables
occupants_data = count_severity(occupants_data, "InjuryStatus Occ Description", "Occupant")
nonmotorist_data = count_severity(nonmotorist_data, "NonMotoristInjurySeverity", "NonMotorist")

# Group by 'Reportnumber' and select the record with the highest-priority severity
processed_occupants_data = (
    occupants_data.sort_values("InjuryStatus Occ Description")
    .groupby("Reportnumber", as_index=False)
    .first()
)

processed_nonmotorist_data = (
    nonmotorist_data.sort_values("NonMotoristInjurySeverity")
    .groupby("Reportnumber", as_index=False)
    .first()
)

def categorize_ped_bike_type(row):
    value = row.get("NonMotoristType")

    if pd.isna(value) or value == "Occupant of Motor Vehicle Not in Transport":
        return "N/A"
    elif value in [
        "Cyclist (Electric)",
        "Cyclist (non-electric)",
        "Scooter (electric)"
    ]:
        return "Bicyclist"
    elif value in [
        "Pedestrian",
        "Other Pedestrian (person in a building, skater, personal conveyance, etc.)",
        "Scooter (non-Electric)",
        "Wheelchair (electric)",
        "Wheelchair (non-electric)"
    ]:
        return "Pedestrian"
    elif value in [
        "Unknown",
        "Unknown Type Of Non-Motorist",
        "Occupant Of a Non-Motor Vehicle Transportation Device",
        "In Animal-Drawn Vehicle",
        "Rider of Animal"
    ]:
        return "Other"
    else:
        return "Other"  # fallback in case there's an unexpected value

processed_nonmotorist_data["NonMotorist_Type_Simple"] = processed_nonmotorist_data.apply(categorize_ped_bike_type, axis=1)

# Export the processed data to a CSV file in the project home folder
processed_occupants_data.to_csv(output_occupants_csv, index=False)
processed_nonmotorist_data.to_csv(output_nonmotorist_csv, index=False)

# Log the output path
arcpy.AddMessage(f"Cleaned Occupants CSV created at: {output_occupants_csv}")
arcpy.AddMessage(f"Cleaned Non-Motorist CSV created at: {output_nonmotorist_csv}")






### PART 2 - Circumstances Table





# Define the updated hierarchy of CircumstancesCode
circumstances_hierarchy = [
    "None",
    "Disregarded Other Traffic Sign",
    "Failed to Keep in Proper Lane",
    "Failed to Yield Right-of-Way",
    "Operated Motor Vehicle in Inattentive, Careless, Negligent, or Erratic Manner",
    "Other",
    "Failure to Obey Traffic Signs, Signals, or Officer",
    "Ran Off Roadway",
    "Disregarded Other Road Markings",
    "Other Improper Action",
    "Glare",
    "Swerved or Avoided Due to Wind, Slippery Surface, Motor Vehicle, Object, Non-Motorist in Roadway, etc.",
    "Improper Turn",
    "Weather Conditions",
    "Too Fast For Conditions",
    "Traffic Control Device",
    "Animal(s)",
    "Ran Red Light",
    "None (No Improper Action)",
    "Steering",
    "Road Surface Condition (wet, icy, snow, slush, etc.)",
    "Regular Congestion",
    "Followed Too Closely",
    "Improper Passing",
    "Over-Correcting/Over-Steering",
    "Operated Motor Vehicle in Reckless or Aggressive Manner",
    "Wrong Side",
    "Wrong Way",
    "Disregard Officer Directions",
    "Ran Stop Sign",
    "Related To a Bus Stop",
    "Ruts, Holes, Bumps",
    "Shoulders (none, low, soft, high)",
    "Visual Obstruction(s)",
    "Other Vehicle Defects",
    "Improper Backing",
    "Debris",
    "Obstruction In Roadway",
    "Prior Crash",
    "Prior Non-Recurring Incident",
    "Work Zone (construction/maintenance/utility)",
    "Worn, Travel-Polished Surface",
    "Brakes",
    "Suspension",
    "Tires",
    "Wheels",
    "Lights (head, signal, tail)",
    "Windows/Windshield",
    "Dart/Dash",
    "Failure to Yield Right-Of-Way",
    "In Roadway Improperly (Standing, Lying, Working, Playing)",
    "Not Visible (Dark Clothing, No Lighting, etc.)",
    "Unknown",
    "Disabled Vehicle-Related (Working on, Pushing, Leaving/Approaching)",
    "Entering/Exiting Parked/Standing Vehicle",
    "Inattentive (Talking, Eating, etc.)",
    "Wrong-Way Riding or Walking",
    "Mirrors",
    "Wipers"
]

contributing_factor_simple = {
    # Unknown
    "None": "Unknown",
    "None (No Improper Action)": "Unknown",
    "Unknown": "Unknown",

    # Animal
    "Animal(s)": "Animal",

    # Distracted
    "Operated Motor Vehicle in Inattentive, Careless, Negligent, or Erratic Manner": "Distracted",
    "Operator Using Cell Phone": "Distracted",
    "Inattentive (Talking, Eating, etc.)": "Distracted",

    # Failure to Obey Traffic Control
    "Failure to Obey Traffic Signs, Signals, or Officer": "Failure to Obey Traffic Control",
    "Ran Red Light": "Failure to Obey Traffic Control",
    "Ran Stop Sign": "Failure to Obey Traffic Control",
    "Disregarded Other Traffic Sign": "Failure to Obey Traffic Control",
    "Disregard Officer Directions": "Failure to Obey Traffic Control",

    # Failed to Yield ROW
    "Failed to Yield Right-of-Way": "Failed to Yield ROW",
    "Failure to Yield Right-Of-Way": "Failed to Yield ROW",

    # Wrong Way
    "Wrong Way": "Wrong way",
    "Wrong Side": "Wrong way",
    "Wrong-Way Riding or Walking": "Wrong way",

    # Speeding
    "Too Fast For Conditions": "Speeding",

    # Aggressive Driving
    "Operated Motor Vehicle in Reckless or Aggressive Manner": "Aggressive Driving",
    "Followed Too Closely": "Aggressive Driving",

    # Environmental Factor
    "Weather Conditions": "Environmental Factor",
    "Road Surface Condition (wet, icy, snow, slush, etc.)": "Environmental Factor",
    "Glare": "Environmental Factor",
    "Visual Obstruction(s)": "Environmental Factor",
    "Not Visible (Dark Clothing, No Lighting, etc.)": "Environmental Factor",

    # Roadway Factor
    "Traffic Control Device": "Roadway Factor",
    "Work Zone (construction/maintenance/utility)": "Roadway Factor",
    "Ruts, Holes, Bumps": "Roadway Factor",
    "Shoulders (none, low, soft, high)": "Roadway Factor",
    "Debris": "Roadway Factor",
    "Obstruction In Roadway": "Roadway Factor",
    "Worn, Travel-Polished Surface": "Roadway Factor",

    # Traffic Congestion
    "Regular Congestion": "Traffic Congestion",
    "Prior Crash": "Traffic Congestion",
    "Prior Non-Recurring Incident": "Traffic Congestion",

    # Ran off Road
    "Ran Off Roadway": "Ran off Road",

    # Other Improper Driver Action
    "Improper Turn": "Other Improper Driver Action",
    "Improper Passing": "Other Improper Driver Action",
    "Improper Backing": "Other Improper Driver Action",
    "Disregarded Other Road Markings": "Other Improper Driver Action",
    "Swerved or Avoided Due to Wind, Slippery Surface, Motor Vehicle, Object, Non-Motorist in Roadway, etc.": "Other Improper Driver Action",
    "Over-Correcting/Over-Steering": "Other Improper Driver Action",
    "Other Improper Action": "Other Improper Driver Action",

    # Vehicle Issue
    "Brakes": "Vehicle Issue",
    "Suspension": "Vehicle Issue",
    "Tires": "Vehicle Issue",
    "Wheels": "Vehicle Issue",
    "Lights (head, signal, tail)": "Vehicle Issue",
    "Windows/Windshield": "Vehicle Issue",
    "Mirrors": "Vehicle Issue",
    "Wipers": "Vehicle Issue",
    "Other Vehicle Defects": "Vehicle Issue",

    # Other
    "Dart/Dash": "Pedestrian Related",
    "Disabled Vehicle-Related (Working on, Pushing, Leaving/Approaching)": "Pedestrian Related",
    "In Roadway Improperly (Standing, Lying, Working, Playing)": "Pedestrian Related",
    "Entering/Exiting Parked/Standing Vehicle": "Pedestrian Related",
    
    # Other
    "Related To a Bus Stop": "Other",
    "Other": "Other"
}



# Import the CSV file
data = pd.read_csv(circumstance_csv)

# Field renaming map
rename_map = {
    "Contribs Description": "CircumstancesCode"
}

# Rename fields if they exist
data = data.rename(columns={old_name: new_name for old_name, new_name in rename_map.items() if old_name in data.columns})

# Apply the mapping function to create the new 'ContributingFactor_Simple' field
data['ContributingFactor_Simple'] = data['CircumstancesCode'].map(contributing_factor_simple)

# Filter out "None" and "Unknown" values
data = data[(data["CircumstancesCode"] != "None") & (data["CircumstancesCode"] != "Unknown")]

# Check for null or empty values in 'ContributingFactor_Simple' and set them to "Unknown"
data['ContributingFactor_Simple'] = data['ContributingFactor_Simple'].fillna('Unknown')

# Process the data
# Ensure CircumstancesCode follows the defined hierarchy
data["CircumstancesCode"] = pd.Categorical(
    data["CircumstancesCode"], categories=circumstances_hierarchy, ordered=True
)

# Group by 'Reportnumber' and select the record with the highest-priority CircumstancesCode
processed_data = (
    data.sort_values("CircumstancesCode")
    .groupby("Reportnumber", as_index=False)
    .first()
)

# Export the processed data to a CSV file in the project home folder
processed_data.to_csv(output_circumstance_csv, index=False)

# Log the output path
arcpy.AddMessage(f"Cleaned Circumstances data CSV created at: {output_circumstance_csv}")





### PART 3 - Vehicle Table







# Define the hierarchy of Vehiclebodytype
vehicle_hierarchy = [
    "Motorcycle", "Moped", "Autocycle", "All-Terrain Vehicle/All-Terrain Cycle (ATV/ATC)", "Moped Or motorized bicycle",
    "Motorcycle - 2 Wheeled", "Motorcycle - 3 Wheeled", "Low Speed Vehicle",
    "Recreational Off-Highway Vehicles (ROV)", "Snowmobile",
    "Bus - School", "Bus - Transit", "Bus - Mini", "Bus - Other Type",
    "Truck - Medium/Heavy 2 Axles Over 10000 LBS",
    "Truck - Cargo Van/Light 2 Axle Over 10000 LBS",
    "Truck - Other Light 10000 LBS or Less",
    "Truck - Tractor",
    "Ambulance/Emergency", "Ambulance/Non-Emergency",
    "Police Vehicle/Emergency", "Police Vehicle/Non-Emergency"
]

# Import the CSV file
data = pd.read_csv(vehicle_csv)

# Field renaming map
rename_map = {
    "SpeedLimit Veh": "Speedlimit",
    "FirstImpact Description": "Firstimpact",
    "RoadAlignment Veh Description": "Roadalignment",
    "RoadGrade Veh Description": "Roadgrade",
    "MostHarmfulEvent Veh Description": "Mostharmfulevent",
    "BodyType Veh Description": "Vehiclebodytype"
}

# Rename fields if they exist
data = data.rename(columns={old_name: new_name for old_name, new_name in rename_map.items() if old_name in data.columns})

# Add a category column based on the hierarchy
data["HierarchyRank"] = data["Vehiclebodytype"].apply(
    lambda x: vehicle_hierarchy.index(x) if x in vehicle_hierarchy else len(vehicle_hierarchy)
)

# Count duplicates for each Reportnumber
data["Vehicles_Involved"] = data.groupby("Reportnumber")["Reportnumber"].transform("count")

# Sort data by HierarchyRank
data = data.sort_values("HierarchyRank")

# Group by Reportnumber and keep the first (highest-priority) record for each group
grouped_data = data.groupby("Reportnumber", as_index=False).first()

# Drop the temporary HierarchyRank column
grouped_data = grouped_data.drop(columns=["HierarchyRank"])

# Export the processed data to a CSV file in the project home folder
grouped_data.to_csv(output_vehicle_csv, index=False)

# Log the output path
arcpy.AddMessage(f"Cleaned Vehicle data CSV created at: {output_vehicle_csv}")








###  PART 4  - Report Table








# Define dictionaries for the mappings
collision_type_simple = {
    "Other": "Other",
    "Unknown": "Unknown",
    "Front to Front": "Head On",
    "Front to Rear": "Rear End",
    "Rear To Rear": "Rear End",
    "Rear To Side": "Rear End",
    "Single Vehicle": "Single Vehicle",
    "Sideswipe, Same Direction": "Sideswipe, Same Direction",
    "Sideswipe, Opposite Direction": "Sideswipe, Opposite Direction",
    "Angle": "Angle"
}

"""
inclement_weather = {
    "Not Applicable": "N/A",
    "N/A": "N/A",
    "Foggy": "Y",
    "Raining": "Y",
    "Severe Winds": "Y",
    "Clear": "N",
    "Cloudy": "N",
    "Snow": "Y",
    "Sleet": "Y",
    "Blowing Snow": "Y",
    "Blowing Sand, Soil, Dirt": "Y",
    "Wintry Mix": "Y",
    "Other": "Unknown",
    "Unknown": "Unknown"
}
"""

surface_condition_simple = {
    "Dry": "Dry",
    "N/A": "Other/NA/Unknown",
    "Null": "Other/NA/Unknown",
    "Wet": "Wet",
    "Unknown": "Other/NA/Unknown",
    "Ice/Frost": "Snow/Ice/Slush",
    "Other": "Other/NA/Unknown",
    "Slush": "Snow/Ice/Slush",
    "Water (standing, moving)": "Wet",
    "Snow": "Snow/Ice/Slush",
    "Mud, Dirt, Gravel": "Other/NA/Unknown",
    "Oil": "Other/NA/Unknown"
}

# Import the CSV file
data = pd.read_csv(report_csv)

# Field renaming map
rename_map = {
    "RoadName": "Road Name",
    "Crashtime": "Timeofcrash",
    "OffroadLocation Description": "Offroaddescription",
    "JunctionRelated Description": "Junction",
    "IntersectingRoadName": "Reference Roadname",
    "FirstHarmEvent Description": "Harmfuleventone",
    "SecondHarmEvent Description": "Harmfuleventtwo",
    "CollisionImpact Description": "Collisiontype",
    "Light Description": "Lighting",
    "Surface Description": "Surfacecondition"
}

# Rename fields if they exist
data = data.rename(columns={old_name: new_name for old_name, new_name in rename_map.items() if old_name in data.columns})

# Add and populate the 'Collision_Type_Simple' field
data['Collision_Type_Simple'] = data['Collisiontype'].map(collision_type_simple)

# Add and populate the 'Inclement_Weather' field
###data['Inclement_Weather'] = data['Weather'].map(inclement_weather)

# Add and populate the 'Surfacecondition_Simple' field
data['Surfacecondition_Simple'] = data['Surfacecondition'].map(surface_condition_simple)

# Handle any missing or null values in the new fields
data['Collision_Type_Simple'] = data['Collision_Type_Simple'].fillna("Other")
###data['Inclement_Weather'] = data['Inclement_Weather'].fillna("Unknown")
data['Surfacecondition_Simple'] = data['Surfacecondition_Simple'].fillna("Other/NA/Unknown")

# Export the cleaned data to a CSV file in the project home folder
data.to_csv(output_report_csv, index=False)

# Log the output path
arcpy.AddMessage(f"Cleaned Report data CSV created at: {output_report_csv}")
