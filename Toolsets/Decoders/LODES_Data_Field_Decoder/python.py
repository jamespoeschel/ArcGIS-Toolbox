import arcpy

# Dictionary of field name patterns and their corresponding aliases
field_alias_dict = {
    "h_geocode": "Residence Census Block Code",
    "w_geocode": "Workplace Census Block Code",
    "C000": "Total Number of Jobs",
    "CA01": "Jobs for workers age under 30",
    "CA02": "Jobs for workers age 30 to 54",
    "CA03": "Jobs for workers age over 54",
    "CE01": "Jobs $1250 month or less",
    "CE02": "Jobs $1251 to $3333 month",
    "CE03": "Jobs greater than $3333 month",
    "CNS01": "Agri Forest Fish Hunting Jobs",
    "CNS02": "Mine Oil Gas Extract Jobs",
    "CNS03": "Utilities Jobs",
    "CNS04": "Construction Jobs",
    "CNS05": "Manufacturing Jobs",
    "CNS06": "Wholesale Trade Jobs",
    "CNS07": "Retail Jobs",
    "CNS08": "Transport and Warehouse Jobs",
    "CNS09": "Information Jobs",
    "CNS10": "Finance and Insurance Jobs",
    "CNS11": "Real Estate Rental Lease Jobs",
    "CNS12": "Professional Science and Tech Jobs",
    "CNS13": "Enterprise Management Jobs",
    "CNS14": "Admin Waste Manage Remediation Jobs",
    "CNS15": "Educational Jobs",
    "CNS16": "Health Care Social Assist Jobs",
    "CNS17": "Art Entertain Recreation Jobs",
    "CNS18": "Accommodation Food Service Jobs",
    "CNS19": "Other Service Jobs",
    "CNS20": "Public Administration Jobs",
    "CR01": "Jobs White Race",
    "CR02": "Jobs Black or AA Race",
    "CR03": "Jobs Native American Race",
    "CR04": "Jobs Asian Race",
    "CR05": "Jobs Pacific Islander Race",
    "CR07": "Jobs Two or More Race",
    "CT01": "Jobs Not Hispanic or Latino",
    "CT02": "Jobs Hispanic or Latino",
    "CD01": "Jobs for Less than High School",
    "CD02": "Jobs for High School Equiv",
    "CD03": "Jobs for Some College or Associates",
    "CD04": "Jobs for Bachelors or Adv Degree",
    "CS01": "Jobs Male",
    "CS02": "Jobs Female",
    "CFA01": "Jobs at Firms aged 0 to 1 Yrs",
    "CFA02": "Jobs at Firms aged 2 to 3 Yrs",
    "CFA03": "Jobs at Firms aged 4 to 5 Yrs",
    "CFA04": "Jobs at Firms aged 6 to 10 Yrs",
    "CFA05": "Jobs at Firms over 10 Yrs old",
    "CFS01": "Jobs at Firm size 0 to 19 employees",
    "CFS02": "Jobs at Firm size 20 to 49 employees",
    "CFS03": "Jobs at Firm size 50 to 249 employees",
    "CFS04": "Jobs at Firm size 250 to 499 employees",
    "CFS05": "Jobs at Firm size 500 plus employees"
}

# Function to update the field alias based on the dictionary
def update_field_alias(Layer_Name):
    try:
        # List all the fields in the feature class/feature layer
        fields = arcpy.ListFields(Layer_Name)
        
        # Logging all field names in the layer
        arcpy.AddMessage("Field Names in the Feature Layer:")
        for field in fields:
            arcpy.AddMessage(field.name)

        # Loop through each field to check for a matching field name pattern
        for field in fields:
            arcpy.AddMessage(f"Processing field: {field.name}")  # Log the current field

            # Check if the field name contains any of the keys in the dictionary
            for key, alias in field_alias_dict.items():
                if key in field.name:
                    try:
                        # Update the alias for the field
                        arcpy.AlterField_management(Layer_Name, field.name, field.aliasName, alias)

    except Exception as e:
        arcpy.AddMessage(f"Error: {e}")

# Script tool entry point
if __name__ == "__main__":
    # Get the input feature class or layer from the parameter
    Layer_Name = arcpy.GetParameterAsText(0)

    # Call the function to update field aliases
    update_field_alias(Layer_Name)
