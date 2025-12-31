# -*- coding: utf-8 -*-
import arcpy
import os

def main():
    # --- PARAMETERS ---
    in_layer = arcpy.GetParameterAsText(0)  # Input Feature Layer
    exclude_fields_raw = arcpy.GetParameterAsText(1)  # Fields to exclude

    # --- PREPARE EXCLUSIONS ---
    if exclude_fields_raw:
        exclude_fields = [f.strip() for f in exclude_fields_raw.split(";") if f.strip()]
    else:
        exclude_fields = []

    arcpy.AddMessage(f"Checking for empty fields in: {in_layer}")
    if exclude_fields:
        arcpy.AddMessage(f"Excluding fields: {', '.join(exclude_fields)}")
    else:
        arcpy.AddMessage("No fields excluded.")

    # --- BACKUP STEP ---
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        default_gdb = aprx.defaultGeodatabase
    except Exception as e:
        arcpy.AddError("Could not access current project or default geodatabase.")
        raise e

    # Determine backup name
    base_name = os.path.basename(in_layer)
    if base_name.lower().endswith(".shp"):
        base_name = os.path.splitext(base_name)[0]
    backup_name = f"{base_name}_backup"

    backup_path = os.path.join(default_gdb, backup_name)

    arcpy.AddMessage(f"Creating backup: {backup_path}")
    arcpy.CopyFeatures_management(in_layer, backup_path)
    arcpy.AddMessage("Backup completed successfully.")

    # --- FIELD CHECKING ---
    all_fields = [
        f.name for f in arcpy.ListFields(in_layer)
        if f.type not in ("OID", "Geometry") and f.name not in exclude_fields
    ]

    arcpy.AddMessage(f"Total fields checked: {len(all_fields)}")

    field_has_value = {f: False for f in all_fields}

    with arcpy.da.SearchCursor(in_layer, all_fields) as cursor:
        for row in cursor:
            for i, val in enumerate(row):
                if val not in (None, "", " "):
                    field_has_value[all_fields[i]] = True
            if all(field_has_value.values()):
                break  # optimization: stop early if all have data

    # --- DETERMINE EMPTY FIELDS ---
    empty_fields = [f for f, has_value in field_has_value.items() if not has_value]

    # --- DELETE EMPTY FIELDS ---
    if empty_fields:
        arcpy.AddMessage(f"Deleting empty fields: {', '.join(empty_fields)}")
        arcpy.DeleteField_management(in_layer, empty_fields)
        arcpy.AddMessage(f"Deleted {len(empty_fields)} empty field(s).")
    else:
        arcpy.AddMessage("No empty fields found to delete.")

    arcpy.AddMessage("Process complete.")


if __name__ == "__main__":
    main()
