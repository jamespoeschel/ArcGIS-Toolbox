import pandas as pd
import arcpy
import os

# Get input parameters
driver_csv = arcpy.GetParameterAsText(0)  # Path to the input CSV file
passenger_csv = arcpy.GetParameterAsText(1)  # Path to the input CSV file
nonmotorist_csv = arcpy.GetParameterAsText(2)  # Path to the input CSV file
circumstance_csv = arcpy.GetParameterAsText(3)  # Path to the input CSV file
vehicle_csv = arcpy.GetParameterAsText(4)  # Path to the input CSV file
report_csv = arcpy.GetParameterAsText(5)  # Path to the input CSV file

# Get the project home folder
home_folder = arcpy.mp.ArcGISProject("CURRENT").homeFolder

# Create the output CSV file name
output_driver_csv = os.path.join(home_folder, "CrashMap_DRIVER_data_cleaned.csv")
output_passenger_csv = os.path.join(home_folder, "CrashMap_PASSENGER_data_cleaned.csv")
output_nonmotorist_csv = os.path.join(home_folder, "CrashMap_NONMOTORIST_data_cleaned.csv")
output_circumstance_csv = os.path.join(home_folder, "CrashMap_CIRCUMSTANCES_data_cleaned.csv")
output_vehicle_csv = os.path.join(home_folder, "CrashMap_VEHICLE_data_cleaned.csv")
output_report_csv = os.path.join(home_folder, "CrashMap_REPORT_data_cleaned.csv")






### PART 1 - Driver, Passenger, NonMotorist Tables






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
driver_data = pd.read_csv(driver_csv)
passenger_data = pd.read_csv(passenger_csv)
nonmotorist_data = pd.read_csv(nonmotorist_csv)

# Ensure severity fields follow the defined hierarchy
driver_data["DriverInjurySeverity"] = pd.Categorical(
    driver_data["DriverInjurySeverity"], categories=severity_hierarchy, ordered=True
)

passenger_data["PassengerInjurySeverity"] = pd.Categorical(
    passenger_data["PassengerInjurySeverity"], categories=severity_hierarchy, ordered=True
)

nonmotorist_data["NonMotoristInjurySeverity"] = pd.Categorical(
    nonmotorist_data["NonMotoristInjurySeverity"], categories=severity_hierarchy, ordered=True
)

# Count severity types and add fields for Driver, Passenger, and Non-Motorist tables
driver_data = count_severity(driver_data, "DriverInjurySeverity", "Driver")
passenger_data = count_severity(passenger_data, "PassengerInjurySeverity", "Passenger")
nonmotorist_data = count_severity(nonmotorist_data, "NonMotoristInjurySeverity", "NonMotorist")

# Group by 'Reportnumber' and select the record with the highest-priority severity
processed_driver_data = (
    driver_data.sort_values("DriverInjurySeverity")
    .groupby("Reportnumber", as_index=False)
    .first()
)

processed_passenger_data = (
    passenger_data.sort_values("PassengerInjurySeverity")
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
    
    if pd.isna(value):
        return "N/A"
    elif value in ["Bicyclist", "Other Pedalcyclist"]:
        return "Bicyclist"
    elif value in ["Pedestrian", "Other Conveyance"]:
        return "Pedestrian"
    elif value in ["Other", "Machine Operator/Rider"]:
        return "Other"
    else:
        return "Other"  # fallback just in case

processed_nonmotorist_data["NonMotorist_Type_Simple"] = processed_nonmotorist_data.apply(categorize_ped_bike_type, axis=1)


# Export the processed data to a CSV file in the project home folder
processed_driver_data.to_csv(output_driver_csv, index=False)
processed_passenger_data.to_csv(output_passenger_csv, index=False)
processed_nonmotorist_data.to_csv(output_nonmotorist_csv, index=False)

# Log the output path
arcpy.AddMessage(f"Cleaned Driver CSV created at: {output_driver_csv}")
arcpy.AddMessage(f"Cleaned Passenger CSV created at: {output_passenger_csv}")
arcpy.AddMessage(f"Cleaned Non-Motorist CSV created at: {output_nonmotorist_csv}")






### PART 2 - Circumstances Table





# Define the full hierarchy of CircumstancesCode
circumstances_hierarchy = [
    "Under Influence of Drugs",
    "Under Influence of Alcohol",
    "Under Influence of Medication",
    "Under Combined Influence",
    "Animal",
    "Wrong Way on One Way Road",
    "Wrong Side of Road",
    "Ran Off the Road",
    "Fell Asleep, Fainted",
    "Physical/Mental Difficulty",
    "Operator Using Cell Phone", #how its written in data
    "Operator Using Cellular Phone", #how its written in data dictionary
    "Exceeded the Speed Limit",
    "Operated Motor Vehicle in Erratic Reckless Manner",
    "Failed to Give Full Time and Attention",
    "Did Not Comply With License Restriction", #how its written in data
    "Did Not Comply with License Restrictions", #how its written in data dictionary
    "Improper Right Turn On Red", #how its written in data
    "Improper Right Turn on Red", #how its written in data dictionary
    "Failed to Yield Right of Way",
    "Failed to Obey Stop Sign",
    "Failed to Obey Traffic Signal",
    "Failed to Obey Other Traffic Control",
    "Failure to Drive Within a Single Lane", 
    "Failed to Keep Right of Center",
    "Failed to Stop for School Bus",
    "Stopping in Lane/Roadway",
    "Too Fast for Conditions",
    "Followed Too Closely",
    "Improper Turn",
    "Improper Lane Change",
    "Improper Backing",
    "Improper Passing",
    "Improper Signal",
    "Improper Parking",
    "Interference/Obstruction by Passenger",
    "Disregarded Other Road Markings",
    "Swerved to Avoid Vehicle or Object in Road",  #how its written in data
    "Swerved or Avoided Vehicle or Object in Road", #how its written in data dictionary
    "Over Correcting/Steering",
    "Over Correcting Over Steering",
    "Other Improper Action",
    "Inattentive",
    "Failure to Obey Traffic Signs Signals or Officer",
    "Backup Due to Prior Crash",
    "Backup Due to Regular Congestion", 
    "Backup Due to Non-Recurring Incident",
    "Non-Highway Work", #how its written in data
    "Non-highway Work", #how its written in data dictionary
    "Wet",
    "Icy or Snow Covered", #how its written in data
    "Icy or Snow-covered", #how its written in data dictionary
    "Debris or Obstruction",
    "Ruts, Holes, Bumps",
    "Road Under Construction", #how its written in data
    "Road Under Construction/Maintenance", #how its written in data dictionary
    "Traffic Control Device Inoperative",
    "Shoulder Low, Soft, High",
    "Physical Obstruction(s)",
    "Worn, Travel-Polished Surface", #how its written in data
    "Worn, Travel-polished Surface", #how its written in data dictionary
    "Smog, Smoke",
    "Sleet, Hail, Freezing rain", #how its written in data
    "Sleet, Hail, Freezing Rain", #how its written in data dictionary
    "Blowing Sand, Soil, Dirt",
    "Severe Crosswinds",
    "Rain, Snow",
    "Physical Obstruction",
    "Vision Obstruction", #how its written in data
    "Vision Obstruction (including blinded by sun)", #how its written in data dictionary
    "Brakes",
    "Tires",
    "Steering",
    "Lights",
    "Windows/Windshield",
    "Wheels", #how its written in data
    "Wheel(s)", #how its written in data dictionary
    "Trailer Coupling", #how its written in data
    "Trailer Uncoupling", #how its written in data dictionary
    "Cargo",
    "Engine Trouble",
    "Suspension",
    "Mirrors",
    "Wipers/Other Environmental", #how its written in data
    "Wipers", #how its written in data dictionary
    "Exhaust/Other Road", #how its written in data
    "Exhaust System", #how its written in data dictionary
    "Other Vehicle Defect",
    "N/A"
]

# Create the dictionary for ContributingFactor_Simple mapping
contributing_factor_simple = {
    "Under Influence of Drugs": "Under Influence of Alcohol, Drugs, or Medication",
    "Under Influence of Alcohol": "Under Influence of Alcohol, Drugs, or Medication",
    "Under Influence of Medication": "Under Influence of Alcohol, Drugs, or Medication",
    "Under Combined Influence": "Under Influence of Alcohol, Drugs, or Medication",
    "Animal": "Animal",
    "Wrong Way on One Way Road": "Wrong way",
    "Wrong Side of Road": "Wrong way",
    "Ran Off the Road": "Ran off Road",
    "Fell Asleep, Fainted": "Asleep or Mental Difficulty",
    "Physical/Mental Difficulty": "Asleep or Mental Difficulty",
    "Operator Using Cell Phone": "Distracted",
    "Operator Using Cellular Phone": "Distracted",
    "Exceeded the Speed Limit": "Speeding",
    "Operated Motor Vehicle in Erratic Reckless Manner": "Aggressive Driving",
    "Failed to Give Full Time and Attention": "Distracted",
    "Did Not Comply With License Restriction": "Other",
    "Did Not Comply with License Restrictions": "Other",
    "Improper Right Turn On Red": "Other Improper Driver Action",
    "Improper Right Turn on Red": "Other Improper Driver Action",
    "Failed to Yield Right of Way": "Failed to Yield ROW",
    "Failed to Obey Stop Sign": "Failure to Obey Traffic Control",
    "Failed to Obey Traffic Signal": "Failure to Obey Traffic Control",
    "Failed to Obey Other Traffic Control": "Failure to Obey Traffic Control",
    "Failure to Drive Within a Single Lane": "Improper Lane Usage/Change",
    "Failed to Keep Right of Center": "Other Improper Driver Action",
    "Failed to Stop for School Bus": "Failure to Obey Traffic Control",
    "Stopping in Lane/Roadway": "Other Improper Driver Action",
    "Too Fast for Conditions": "Speeding",
    "Followed Too Closely": "Aggressive Driving",
    "Improper Turn": "Other Improper Driver Action",
    "Improper Lane Change": "Improper Lane Usage/Change",
    "Improper Backing": "Other Improper Driver Action",
    "Improper Passing": "Other Improper Driver Action",
    "Improper Signal": "Other Improper Driver Action",
    "Improper Parking": "Other Improper Driver Action",
    "Interference/Obstruction by Passenger": "Other",
    "Disregarded Other Road Markings": "Other Improper Driver Action",
    "Swerved to Avoid Vehicle or Object in Road": "Other Improper Driver Action",
    "Swerved or Avoided Vehicle or Object in Road": "Other Improper Driver Action",
    "Over Correcting/Steering": "Other Improper Driver Action",
    "Over Correcting Over Steering": "Other Improper Driver Action",
    "Other Improper Action": "Other Improper Driver Action",
    "Inattentive": "Distracted",
    "Failure to Obey Traffic Signs Signals or Officer": "Failure to Obey Traffic Control",
    "Backup Due to Prior Crash": "Traffic Congestion",
    "Backup Due to Regular Congestion": "Traffic Congestion",
    "Backup Due to Non-Recurring Incident": "Traffic Congestion",
    "Road Under Construction": "Roadway Factor",
    "Non-Highway Work": "Roadway Factor",
    "Non-highway Work": "Roadway Factor",
    "Wet": "Environmental Factor",
    "Icy or Snow Covered": "Environmental Factor",
    "Icy or Snow-covered": "Environmental Factor",
    "Debris or Obstruction": "Roadway Factor",
    "Ruts, Holes, Bumps": "Roadway Factor",
    "Road Under Construction": "Roadway Factor",
    "Road Under Construction/Maintenance": "Roadway Factor",
    "Traffic Control Device Inoperative": "Roadway Factor",
    "Shoulder Low, Soft, High": "Roadway Factor",
    "Physical Obstruction(s)": "Roadway Factor",
    "Worn, Travel-Polished Surface": "Roadway Factor",
    "Worn, Travel-polished Surface": "Roadway Factor",
    "Smog, Smoke": "Environmental Factor",
    "Sleet, Hail, Freezing rain": "Environmental Factor",
    "Sleet, Hail, Freezing Rain": "Environmental Factor",
    "Blowing Sand, Soil, Dirt": "Environmental Factor",
    "Severe Crosswinds": "Environmental Factor",
    "Rain, Snow": "Environmental Factor",
    "Physical Obstruction": "Environmental Factor",
    "Vision Obstruction": "Environmental Factor",
    "Vision Obstruction (including blinded by sun)": "Environmental Factor",
    "Brakes": "Vehicle Issue",
    "Tires": "Vehicle Issue",
    "Steering": "Vehicle Issue",
    "Lights": "Vehicle Issue",
    "Windows/Windshield": "Vehicle Issue",
    "Wheels": "Vehicle Issue",
    "Wheel(s)": "Vehicle Issue",
    "Trailer Coupling": "Vehicle Issue",
    "Trailer Uncoupling": "Vehicle Issue",
    "Cargo": "Vehicle Issue",
    "Engine Trouble": "Vehicle Issue",
    "Suspension": "Vehicle Issue",
    "Mirrors": "Vehicle Issue",
    "Wipers/Other Environmental": "Vehicle Issue",
    "Wipers": "Vehicle Issue",
    "Exhaust/Other Road": "Vehicle Issue",
    "Exhaust System": "Vehicle Issue",
    "Other Vehicle Defect": "Vehicle Issue",
    "N/A": "Unknown"
}

# Import the CSV file
data = pd.read_csv(circumstance_csv)

# Apply the mapping function to create the new 'ContributingFactor_Simple' field
data['ContributingFactor_Simple'] = data['CircumstancesCode'].map(contributing_factor_simple)

# Filter out "N/A" values
data = data[data["CircumstancesCode"] != "N/A"]

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
    "Motorcycle", "Moped", "Autocycle",
    "Truck - Medium/Heavy 2 Axles Over 10000 LBS",
    "Truck - Cargo Van/Light 2 Axle Over 10000 LBS",
    "Truck - Other Light 10000 LBS or Less",
    "Truck - Tractor",
    "Ambulance/Emergency", "Ambulance/Non-Emergency",
    "Police Vehicle/Emergency", "Police Vehicle/Non-Emergency"
]

# Define the dictionary for Vehiclemovement with integer keys
vehicle_movement_dict = {
    0: "Not Applicable",
    1: "Moving Constant Speed",
    2: "Accelerating",
    3: "Slowing or Stopping",
    4: "Starting From Lane",
    5: "Starting From Parked",
    6: "Stopped in Traffic Lane",
    7: "Changing Lanes",
    8: "Passing",
    9: "Parking",
    10: "Parked",
    11: "Backing",
    12: "Making Left Turn",
    13: "Making Right Turn",
    14: "Right Turn on Red",
    15: "Making U Turn",
    16: "Skidding",
    17: "Driverless Moving Vehicle",
    18.07: "Leaving Traffic Lane",
    19.07: "Entering Traffic Lane",
    20.03: "Negotiating a Curve",
    88: "Other",
    99: "Unknown"
}

# Import the CSV file
data = pd.read_csv(vehicle_csv)

# Add the VehicleMovement_Text field if Vehiclemovement exists
if "Vehiclemovement" in data.columns:
    # Convert Vehiclemovement to numeric (if not already numeric), handling errors by coercing invalid values
    data["Vehiclemovement"] = pd.to_numeric(data["Vehiclemovement"], errors='coerce')

    # Map to dictionary with numeric keys and fill missing values with "Unknown"
    data["VehicleMovement_Text"] = data["Vehiclemovement"].map(vehicle_movement_dict).fillna("Unknown")

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
    "Not Applicable": "Other",
    "Head On": "Head On",
    "Angle Meets Left Head On": "Head On",
    "Head On Left Turn": "Head On",
    "Angle Meets Left Turn Head On": "Head On",
    "Same Direction Rear End Right Turn": "Rear End",
    "Same Direction Rear End Left Turn": "Rear End",
    "Same Direction Rear End": "Rear End",
    "Opposite Direction Sideswipe": "Opposite Direction Sideswipe",
    "Same Direction Sideswipe": "Same Direction Sideswipe",
    "Same Direction Right Turn": "Same Direction Sideswipe",
    "Same Direction Left Turn": "Same Direction Sideswipe",
    "Same Direction Both Left Turn": "Same Direction Sideswipe",
    "Opposite Direction Both Left Turn": "Opposite Direction Sideswipe",
    "Same Movement Angle": "Angle",
    "Angle Meets Right Turn": "Angle",
    "Angle Meets Left Turn": "Angle",
    "Straight Movement Angle": "Angle",
    "Single Vehicle": "Single Vehicle",
    "N/A": "Other",
    "Other": "Other",
    "Unknown": "Other"
}

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

surface_condition_simple = {
    "Dry": "Dry",
    "N/A": "Other/NA/Unknown",
    "Null": "Other/NA/Unknown",
    "Wet": "Wet",
    "Unknown": "Other/NA/Unknown",
    "Ice": "Snow/Ice/Slush",
    "Other": "Other/NA/Unknown",
    "Slush": "Snow/Ice/Slush",
    "Water (Standing, Moving)": "Wet",
    "Snow": "Snow/Ice/Slush",
    "Mud, Dirt, Gravel": "Other/NA/Unknown",
    "Oil": "Other/NA/Unknown"
}

# Import the CSV file
data = pd.read_csv(report_csv)

# Add and populate the 'Collision_Type_Simple' field
data['Collision_Type_Simple'] = data['Collisiontype'].map(collision_type_simple)

# Add and populate the 'Inclement_Weather' field
data['Inclement_Weather'] = data['Weather'].map(inclement_weather)

# Add and populate the 'Surfacecondition_Simple' field
data['Surfacecondition_Simple'] = data['Surfacecondition'].map(surface_condition_simple)

# Handle any missing or null values in the new fields
data['Collision_Type_Simple'] = data['Collision_Type_Simple'].fillna("Other")
data['Inclement_Weather'] = data['Inclement_Weather'].fillna("Unknown")
data['Surfacecondition_Simple'] = data['Surfacecondition_Simple'].fillna("Other/NA/Unknown")

# Export the cleaned data to a CSV file in the project home folder
data.to_csv(output_report_csv, index=False)

# Log the output path
arcpy.AddMessage(f"Cleaned Report data CSV created at: {output_report_csv}")
