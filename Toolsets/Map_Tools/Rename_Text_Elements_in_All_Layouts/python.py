# -*- coding: utf-8 -*-
import arcpy

arcpy.env.overwriteOutput = True

aprx = arcpy.mp.ArcGISProject("CURRENT")

layout_count = 0
renamed_static = 0
service_credits_found = 0
skipped_dynamic = 0

for layout in aprx.listLayouts():
    layout_count += 1
    arcpy.AddMessage(f"Processing layout: {layout.name}")

    for elm in layout.listElements("TEXT_ELEMENT"):

        txt = elm.text or ""

        # --------------------------------------------
        # Case 1: Service Layer Credits dynamic text
        # --------------------------------------------
        if (
            txt.lstrip().startswith("<dyn")
            and 'property="serviceLayerCredits"' in txt
        ):
            try:
                elm.name = "Service layer Credits"
                elm.locked = True
                service_credits_found += 1
                arcpy.AddMessage(
                    "  Named and locked Service layer Credits element"
                )
            except Exception as e:
                arcpy.AddWarning(
                    f"  Could not update Service layer Credits element: {e}"
                )
            continue

        # --------------------------------------------
        # Case 2: Any other dynamic text → skip
        # --------------------------------------------
        if txt.lstrip().startswith("<dyn"):
            skipped_dynamic += 1
            arcpy.AddMessage("  Skipped other dynamic text element")
            continue

        # --------------------------------------------
        # Case 3: Static text → rename as before
        # --------------------------------------------
        try:
            elm.name = txt
            renamed_static += 1
            arcpy.AddMessage(f"  Renamed text element to: {elm.name}")
        except Exception as e:
            arcpy.AddWarning(
                f"  Could not rename text element in layout '{layout.name}': {e}"
            )

arcpy.AddMessage(
    f"Finished processing {layout_count} layouts.\n"
    f"  Static text renamed: {renamed_static}\n"
    f"  Service layer Credits updated: {service_credits_found}\n"
    f"  Other dynamic text skipped: {skipped_dynamic}"
)
