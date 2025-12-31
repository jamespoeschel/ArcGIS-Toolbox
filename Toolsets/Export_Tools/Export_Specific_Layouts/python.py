#Contributors: James Poeschel 

import arcpy
import os

# Get the current project
aprx = arcpy.mp.ArcGISProject("CURRENT")

# Get parameters from the tool
layoutList = arcpy.GetParameterAsText(0)
exportFormat = arcpy.GetParameterAsText(1)
exportRes = arcpy.GetParameterAsText(2)
figFolder = arcpy.GetParameterAsText(3)

# Make sure the output folder ends with a path separator
if not figFolder.endswith(os.sep):
    figFolder += os.sep

# Split the user input into a list
selected_layouts = layoutList.split(';')

# Validate export format
valid_export_formats = ['png', 'jpg', 'pdf', 'aix']
if exportFormat.lower() not in valid_export_formats:
    arcpy.AddError(f"Invalid export format: {exportFormat}")
    quit()

# Strip any leading or trailing spaces from the layout names and create a set
selected_layouts = {layout.strip() for layout in selected_layouts if layout.strip()}

# Check for spaces in layout names and add a warning message
for layout in selected_layouts:
    if ' ' in layout:
        arcpy.AddWarning(f"The layout name '{layout}' contains spaces. Please rename to remove or replace the spaces.")

# Debug: print selected layouts
arcpy.AddMessage(f"Selected layouts: {selected_layouts}")

# Iterate through all layouts in the project
for lyt in aprx.listLayouts():
    
    # Check if the layout is in the selected layouts set
    if lyt.name in selected_layouts:
        arcpy.AddMessage(f"Found layout: {lyt.name}")
        outputFilePath = os.path.join(figFolder, f"{lyt.name}.{exportFormat.lower()}")
        
        # Determine the export function based on the chosen format
        try:
            if exportFormat.lower() == "png":
                lyt.exportToPNG(outputFilePath, resolution=int(exportRes))
                arcpy.AddMessage(f"Exported {lyt.name} to {outputFilePath}")
            elif exportFormat.lower() == "jpg":
                lyt.exportToJPEG(outputFilePath, resolution=int(exportRes))
                arcpy.AddMessage(f"Exported {lyt.name} to {outputFilePath}")
            elif exportFormat.lower() == "pdf":
                lyt.exportToPDF(outputFilePath, resolution=int(exportRes))
                arcpy.AddMessage(f"Exported {lyt.name} to {outputFilePath}")
            elif exportFormat.lower() == "aix":
                lyt.exportToAIX(outputFilePath, resolution=int(exportRes))
                arcpy.AddMessage(f"Exported {lyt.name} to {outputFilePath}")
        except Exception as e:
            arcpy.AddError(f"Failed to export {lyt.name} to {outputFilePath}: {str(e)}")
