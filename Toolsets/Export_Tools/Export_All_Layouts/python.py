import arcpy
import os

aprx = arcpy.mp.ArcGISProject("CURRENT")
figFolder = arcpy.GetParameterAsText(0)
exportFormat = arcpy.GetParameterAsText(1)
exportRes = arcpy.GetParameterAsText(2)

# Make sure the output folder ends with a path separator
if not figFolder.endswith(os.sep):
    figFolder += os.sep

for lyt in aprx.listLayouts():
    print(f" {lyt.name} ({lyt.pageHeight} x {lyt.pageWidth} {lyt.pageUnits})")
    
    # Construct the output file path using os.path.join
    outputFilePath = os.path.join(figFolder, f"{lyt.name}.{exportFormat.lower()}")
    
    # Determine the export function based on the chosen format
    if exportFormat.lower() == "png":
        lyt.exportToPNG(outputFilePath, resolution=int(exportRes))
    elif exportFormat.lower() == "jpg":
        lyt.exportToJPEG(outputFilePath, resolution=int(exportRes))
    elif exportFormat.lower() == "pdf":
        lyt.exportToPDF(outputFilePath, resolution=int(exportRes))
    elif exportFormat.lower() == "aix":
        lyt.exportToAIX(outputFilePath, resolution=int(exportRes))
    else:
        print(f"Invalid export format: {exportFormat}")
