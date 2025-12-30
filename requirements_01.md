# Purpose
Create test data with known content for testing other python programs
Edit the script "fc_profiler_create_testdata.py"
Keep the solution to a single file.
Follow the style in this script, use its existing logging framework.

Use arcpy.management.CreateFileGDB to create a geodatabase.
Use arcpy.management.CreateFeatureclass to create a feature class.
Use arcpy.da.InsertCursor to add records to a feature class.

The script will not accept any args.  The path to the GDB and its name will be hardcoded.

Config:
Hardcode these parameters in the parameters section of the code:
gdb_location = r"C:\Users\Mic\OneDrive\code\py_arcpy\fc_profiler_testdata"
gdb_name = "fc_profiler_testdata.gdb"
arcpy.env.overwriteOutput=True
arcpy.env.addOutputsToMap=False

# Geodatabase
Create the geodatabase "fc_profiler_testdata.gdb"
If "fc_profiler_testdata.gdb" exists, delete the .gdb folder with arcpy.management.Delete() (or shutil.rmtree only if Delete fails), then recreate.

# Feature Class Types
In "fc_profiler_testdata.gdb" create the Point feature class "fc_pt" using EPSG 3857, no rows are required.
In "fc_profiler_testdata.gdb" create the Line feature class "fc_pl" using EPSG 3857, no rows are required.
In "fc_profiler_testdata.gdb" create the Polygon feature class "fc_pg" using EPSG 3857, no rows are required.
In "fc_profiler_testdata.gdb" create the Multipoint feature class "fc_mpt" using EPSG 3857, no rows are required.
In "fc_profiler_testdata.gdb" create the Multipatch feature class "fc_mp" using EPSG 3857, no rows are required.


# Row count tests

## Rows_0_pt
In "fc_profiler_testdata.gdb" create the point feature class "Rows_0_pt" using EPSG 3857. Create FC only; no rows are required.

## Rows_1_pt
In fc_profiler_testdata.gdb create the point feature class "Rows_1_pt" using EPSG 3857. Add one point record at the location (0,0).

## Rows_9_pt
In fc_profiler_testdata.gdb create the point feature class "Rows_9_pt" using EPSG 3857. Create the first point at (0, 0), then eight points with 1m x spacing at (1,0), (2,0)…(8,0).

# EPSG 
In "fc_profiler_testdata.gdb" create the point feature class "EPSG_3857_pt" using EPSG 3857, no rows are required.
In "fc_profiler_testdata.gdb" create the point feature class "EPSG_4283_pt" using EPSG 4283, no rows are required.
In "fc_profiler_testdata.gdb" create the point feature class "EPSG_7856_pt" using EPSG 7856, no rows are required.

# Z and M

In "fc_profiler_testdata.gdb" create the point feature class "ZM_NoZNoM_pt" using EPSG 3857, no rows are required.
In "fc_profiler_testdata.gdb" create the point feature class "ZM_HasZ_pt" using EPSG 3857, z-values enabled, m-values disabled, no rows are required.
In "fc_profiler_testdata.gdb" create the point feature class "ZM_HasM_pt" using EPSG 3857, m-values enabled, z-values disabled, no rows are required.
In "fc_profiler_testdata.gdb" create the point feature class "ZM_HasZM_pt" using EPSG 3857, z-values enabled AND m-values enabled, no rows are required.


# Empty State 
In "fc_profiler_testdata.gdb" create the point feature class "EmptyState_pt" using EPSG 3857.
In "EmptyState_pt" add a text field "Key" as Text 10 chars.
In "EmptyState_pt" add a text field "Value" as Text 10 chars.
To "EmptyState_pt":
- Add 1 record with Key = "Null", Value is Null
- Add 1 record with Key = "Zero length string", Value = ""
- Add 1 record with Key = "A space", Value = " "
- Add 1 record with Key = "Tab character", Value = \t
- Add 1 record with Key = "Newline character", Value = \n
- Add 1 record with Key = "Carriage return character", Value = \r
- Add 1 record with Key = "Invisible unicode character", Value = U+200B
- Add 1 record with Key = "Non-Breaking Space", Value = U+00A0
- Add 1 record with Key = "Zero-Width No-Break Space", Value = U+FEFF

Note that these are literal characters (tab/newline/CR) and that U+200B etc. must be inserted as actual Unicode characters (not the string "U+200B").
Tab value must be "\t" (a literal tab character in the Python string)
Newline value must be "\n"
Carriage return value must be "\r"
U+200B must be "\u200b", U+00A0 must be "\u00a0", U+FEFF must be "\ufeff"
Log the repr(value) as log.info during creation as a debugging aid when insering these rows

# Validation Checks

Write functions to perform the following checks:
- Confirm GDB exists
- Confirm all required feature classes exist
- Confirm row counts match: Rows_0_pt=0, Rows_1_pt=1, Rows_9_pt=9
- Confirm spatial references: EPSG 3857/4283/7856 applied
- Confirm the Feature Class "ZM_NoZNoM_pt" has no z-values 
- Confirm the Feature Class "ZM_NoZNoM_pt" has no m-values 
- Confirm the Feature Class "ZM_HasZ_pt" has z-values 
- Confirm the Feature Class "ZM_HasM_pt" has m-values
- Confirm the Feature Class "ZM_HasZM_pt" has z-values 
- Confirm the Feature Class "ZM_HasZM_pt" has m-values
- Confirm the Feature Class "EmptyState_pt" has 9 rows
- Confirm the Feature Class "EmptyState_pt" has the field "Key"
- Confirm the Feature Class "EmptyState_pt" has the field "Value"

- Confirm the Feature Class "fc_pt" has Shape type Point
- Confirm the Feature Class "fc_pl" has Shape type Line
- Confirm the Feature Class "fc_pg" has Shape type Polygon
- Confirm the Feature Class "fc_mpt" has Shape type Multipoint
- Confirm the Feature Class "fc_mp" has Shape type Multipatch


Validation functions must raise ValueError (or a custom exception) if any check fails, and log a clear error showing expected vs actual
Use arcpy.Describe(fc) to check for z-values and m-values


# End of Requirements #