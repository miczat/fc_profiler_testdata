""" 
Creates test data for feature class profiler.


Args:
    parameter: description
    parameter: description

Preconditions:
    Statements that must be true before running the program.


Postconditions
    Statements that will be true after running the program.


Returned values
    What is returned by the program, if anything.

Issues and known limitations:
    Writen for Python 3.13.7 as shipped with ArcGIS Pro 3.6.0

Dev Notes:
    Remote origin: https://github.com/miczat/python-script-template

    Terminology, with pathlib name:
       image_path   =  C:\TEMP\A.JPG     # full path 'p'
       image_folderpath =  C:\TEMP       # p.parent
       image_foldername =  TEMP          # p.parent.name
       image_filename   =  A.JPG         # p.name
       image_name       =  A             # p.stem
       image_extension  =  JPG           # p.suffix   
     
"""
__author__ = "Mic Zatorsky"
__version__ = '2.0'
LAST_UPDATED = "2025-12-30"


import arcpy  # pyright: ignore[reportMissingImports]
from arcpy import env # pyright: ignore[reportMissingImports]
import logging
import os
import datetime
import sys
import traceback
from pathlib import Path    
import shutil



log = logging.getLogger(__name__)

# -----------------------------------------
# run config
# -----------------------------------------
log_name = r"fc_profiler_testdata"
log_folder = r"."


# input parameters
gdb_location = r"C:\Users\Mic\OneDrive\code\py_arcpy\fc_profiler_testdata"
gdb_name = "fc_profiler_testdata.gdb"

# output parameters

# other config
env.overwriteOutput = True
env.addOutputsToMap = False
env.workspace = gdb_location

# set the geoprocessing environment



# -----------------------------------------
# create and configure the logger
# -----------------------------------------

def flatten_for_csv(text: str) -> str:
    """Make a message safe for one-line CSV logging."""
    return (
        text.replace('"', "''")    # avoid breaking our quoted "message" column
            .replace('\r', '\\r')  # show newlines explicitly
            .replace('\n', '\\n')
    )



def setup_logger(log_folder: str) -> None:
    """Configure logging to a CSV file and the console.

    Args:
        log_folder: Folder where the log file will be written.

    Raises:
        PermissionError: If the log file is open in another app.
        OSError: For other I/O-related errors.
    """
    if log.handlers:
        # Logger already configured
        return

    logfile_ext = ".log.csv"
    logfile = os.path.join(log_folder, log_name + logfile_ext)

    # Decide if we need to write a header row
    new_file = not os.path.exists(logfile) or os.path.getsize(logfile) == 0

    # Common formatter for both file and console
    d = ","
    log_msg_format_str = (
        f"%(asctime)s{d}%(levelname)s{d}%(filename)s{d}%(funcName)s{d}\"%(message)s\""
    )
    datetime_fmt_str = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_msg_format_str, datetime_fmt_str)

    # File handler
    try:
        fh = logging.FileHandler(filename=logfile, mode="a", encoding="utf-8")
    except PermissionError as pe:
        print(
            "The log file could not be written due to permissions. "
            "Check if it is open in Excel or another app. Program stopping."
        )
        print(repr(pe))
        raise
    except OSError as oe:
        print("Some other I/O-related error occurred. Program stopping.")
        print(repr(oe))
        raise
    except Exception as e:
        print("An unexpected error occurred while configuring logging. Program stopping.")
        print(repr(e))
        raise

    if new_file:
        fh.stream.write("timestamp,level,filename,funcName,message\n")
        fh.flush()

    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # Console handler (same verbose format for copy-paste to Excel)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    log.setLevel(logging.DEBUG)


# -----------------------------------------
# get row count
# -----------------------------------------
def get_row_count(table_or_layer) -> int:
    """Return the number of rows in a table or feature layer.

    Args:
        table_or_layer: Table or feature layer path, name, or object accepted
            by arcpy.GetCount_management. This can be, for example, a feature
            class path, an in-memory layer name, or a layer object.

    Returns:
        int: Number of rows in the input dataset.

    Raises:
        arcpy.ExecuteError: If the underlying geoprocessing tool fails.
        RuntimeError: If ArcPy is not initialized or the workspace is invalid.
    """
    row_count = int(arcpy.GetCount_management(table_or_layer)[0])
    log.debug(f"{row_count} rows in {table_or_layer}")
    return row_count


def get_spatial_reference(epsg_code: int) -> arcpy.SpatialReference:
    """Return a spatial reference for the provided EPSG code."""
    spatial_ref = arcpy.SpatialReference(epsg_code)
    if spatial_ref.factoryCode != epsg_code:
        raise ValueError(
            f"Spatial reference mismatch for EPSG {epsg_code}: "
            f"factoryCode={spatial_ref.factoryCode}"
        )
    return spatial_ref


def delete_if_exists(path: Path) -> None:
    """Delete a geodatabase if it exists."""
    if arcpy.Exists(str(path)):
        log.info(f"Deleting existing geodatabase: {path}")
        try:
            arcpy.management.Delete(str(path))
        except arcpy.ExecuteError:
            log.warning("arcpy.management.Delete failed; clearing cache and retrying.")
            arcpy.ClearWorkspaceCache_management()
            try:
                arcpy.management.Delete(str(path))
            except arcpy.ExecuteError:
                log.warning("Retry failed; attempting shutil.rmtree.")
                if path.exists() and path.is_dir():
                    shutil.rmtree(path)
        if arcpy.Exists(str(path)):
            raise ValueError(f"Failed to delete geodatabase: {path}")


def create_geodatabase(gdb_location_path: Path, gdb_name_value: str) -> Path:
    """Create the file geodatabase and return its path."""
    gdb_path = gdb_location_path / gdb_name_value
    delete_if_exists(gdb_path)
    log.info(f"Creating geodatabase: {gdb_path}")
    arcpy.management.CreateFileGDB(str(gdb_location_path), gdb_name_value)
    if not arcpy.Exists(str(gdb_path)):
        raise ValueError(f"Geodatabase not created: {gdb_path}")
    return gdb_path


def create_feature_class(
    gdb_path: Path,
    fc_name: str,
    geometry_type: str,
    spatial_ref: arcpy.SpatialReference,
    has_z: bool = False,
    has_m: bool = False
) -> Path:
    """Create a feature class with the specified geometry type and spatial ref."""
    log.info(
        f"Creating feature class {fc_name} ({geometry_type}) "
        f"Z={has_z} M={has_m} SR={spatial_ref.factoryCode}"
    )
    fc_path = gdb_path / fc_name
    arcpy.management.CreateFeatureclass(
        out_path=str(gdb_path),
        out_name=fc_name,
        geometry_type=geometry_type,
        spatial_reference=spatial_ref,
        has_z="ENABLED" if has_z else "DISABLED",
        has_m="ENABLED" if has_m else "DISABLED",
    )
    if not arcpy.Exists(str(fc_path)):
        raise ValueError(f"Feature class not created: {fc_path}")
    return fc_path


def insert_point_rows(fc_path: Path, points_xy: list[tuple[float, float]]) -> None:
    """Insert point records into a feature class."""
    if not points_xy:
        return
    log.info(f"Inserting {len(points_xy)} points into {fc_path.name}")
    with arcpy.da.InsertCursor(str(fc_path), ["SHAPE@XY"]) as cursor:
        for point in points_xy:
            cursor.insertRow([point])


def create_empty_state_rows(fc_path: Path) -> None:
    """Create fields and insert empty state test rows."""
    log.info(f"Adding fields to {fc_path.name}")
    arcpy.management.AddField(str(fc_path), "Key", "TEXT", field_length=50)
    arcpy.management.AddField(str(fc_path), "Value", "TEXT", field_length=10)

    rows = [
        ("Null", None),
        ("Zero length string", ""),
        ("A space", " "),
        ("Tab character", "\t"),
        ("Newline character", "\n"),
        ("Carriage return character", "\r"),
        ("Invisible unicode character", "\u200b"),
        ("Non-Breaking Space", "\u00a0"),
        ("Zero-Width No-Break Space", "\ufeff"),
    ]
    with arcpy.da.InsertCursor(str(fc_path), ["Key", "Value"]) as cursor:
        for key, value in rows:
            log.info(f"EmptyState {key}: repr(Value)={repr(value)}")
            cursor.insertRow([key, value])


def validate_gdb_exists(gdb_path: Path) -> None:
    if not arcpy.Exists(str(gdb_path)):
        message = f"GDB missing: expected {gdb_path}"
        log.error(message)
        raise ValueError(message)


def validate_feature_classes_exist(gdb_path: Path, feature_classes: list[str]) -> None:
    missing = []
    for fc_name in feature_classes:
        fc_path = gdb_path / fc_name
        if not arcpy.Exists(str(fc_path)):
            missing.append(fc_name)
    if missing:
        message = f"Missing feature classes: {missing}"
        log.error(message)
        raise ValueError(message)


def validate_row_counts(gdb_path: Path, expected_counts: dict[str, int]) -> None:
    for fc_name, expected in expected_counts.items():
        fc_path = gdb_path / fc_name
        actual = get_row_count(str(fc_path))
        if actual != expected:
            message = f"Row count mismatch {fc_name}: expected {expected}, got {actual}"
            log.error(message)
            raise ValueError(message)


def validate_spatial_reference(gdb_path: Path, expected_epsg: dict[str, int]) -> None:
    for fc_name, expected in expected_epsg.items():
        fc_path = gdb_path / fc_name
        desc = arcpy.Describe(str(fc_path))
        actual = desc.spatialReference.factoryCode
        if actual != expected:
            message = f"Spatial reference mismatch {fc_name}: expected {expected}, got {actual}"
            log.error(message)
            raise ValueError(message)


def validate_zm_flags(
    gdb_path: Path,
    expected_flags: dict[str, tuple[bool, bool]]
) -> None:
    for fc_name, (expected_z, expected_m) in expected_flags.items():
        fc_path = gdb_path / fc_name
        desc = arcpy.Describe(str(fc_path))
        if not hasattr(desc, "hasZ") or not hasattr(desc, "hasM"):
            message = f"Describe missing hasZ/hasM for {fc_name}"
            log.error(message)
            raise ValueError(message)
        actual_z = desc.hasZ
        actual_m = desc.hasM
        if actual_z != expected_z:
            message = (
                f"Z flag mismatch {fc_name}: expected {expected_z}, got {actual_z}"
            )
            log.error(message)
            raise ValueError(message)
        if actual_m != expected_m:
            message = (
                f"M flag mismatch {fc_name}: expected {expected_m}, got {actual_m}"
            )
            log.error(message)
            raise ValueError(message)


def validate_fields(gdb_path: Path, fc_name: str, required_fields: list[str]) -> None:
    fc_path = gdb_path / fc_name
    field_names = {field.name for field in arcpy.ListFields(str(fc_path))}
    missing = [field for field in required_fields if field not in field_names]
    if missing:
        message = f"Missing fields in {fc_name}: {missing}"
        log.error(message)
        raise ValueError(message)


def validate_shape_types(gdb_path: Path, expected_shapes: dict[str, str]) -> None:
    for fc_name, expected_shape in expected_shapes.items():
        fc_path = gdb_path / fc_name
        desc = arcpy.Describe(str(fc_path))
        actual = desc.shapeType
        if actual != expected_shape:
            message = f"Shape type mismatch {fc_name}: expected {expected_shape}, got {actual}"
            log.error(message)
            raise ValueError(message)


def validate_all(gdb_path: Path) -> None:
    """Run all validation checks."""
    validate_gdb_exists(gdb_path)
    all_feature_classes = [
        "fc_pt",
        "fc_pl",
        "fc_pg",
        "fc_mpt",
        "fc_mp",
        "Rows_0_pt",
        "Rows_1_pt",
        "Rows_9_pt",
        "EPSG_3857_pt",
        "EPSG_4283_pt",
        "EPSG_7856_pt",
        "ZM_NoZNoM_pt",
        "ZM_HasZ_pt",
        "ZM_HasM_pt",
        "ZM_HasZM_pt",
        "EmptyState_pt",
    ]
    validate_feature_classes_exist(gdb_path, all_feature_classes)
    validate_row_counts(
        gdb_path,
        {
            "Rows_0_pt": 0,
            "Rows_1_pt": 1,
            "Rows_9_pt": 9,
            "EmptyState_pt": 9,
        },
    )
    validate_spatial_reference(
        gdb_path,
        {
            "EPSG_3857_pt": 3857,
            "EPSG_4283_pt": 4283,
            "EPSG_7856_pt": 7856,
        },
    )
    validate_zm_flags(
        gdb_path,
        {
            "ZM_NoZNoM_pt": (False, False),
            "ZM_HasZ_pt": (True, False),
            "ZM_HasM_pt": (False, True),
            "ZM_HasZM_pt": (True, True),
        },
    )
    validate_fields(gdb_path, "EmptyState_pt", ["Key", "Value"])
    validate_shape_types(
        gdb_path,
        {
            "fc_pt": "Point",
            "fc_pl": "Polyline",
            "fc_pg": "Polygon",
            "fc_mpt": "Multipoint",
            "fc_mp": "Multipatch",
        },
    )


# -----------------------------------------
# main
# -----------------------------------------

def main():
    """main"""
    start_time = datetime.datetime.now()
    log.info('Start')
    log.info(f"Script version {__version__}, by {__author__} last updated {LAST_UPDATED}")
    log.info(f"Using Python version {sys.version}")

    try:
        log.info("Trying...")
        gdb_location_path = Path(gdb_location)
        gdb_path = create_geodatabase(gdb_location_path, gdb_name)

        sr_3857 = get_spatial_reference(3857)
        sr_4283 = get_spatial_reference(4283)
        sr_7856 = get_spatial_reference(7856)

        create_feature_class(gdb_path, "fc_pt", "POINT", sr_3857)
        create_feature_class(gdb_path, "fc_pl", "POLYLINE", sr_3857)
        create_feature_class(gdb_path, "fc_pg", "POLYGON", sr_3857)
        create_feature_class(gdb_path, "fc_mpt", "MULTIPOINT", sr_3857)
        create_feature_class(gdb_path, "fc_mp", "MULTIPATCH", sr_3857)

        create_feature_class(gdb_path, "Rows_0_pt", "POINT", sr_3857)
        rows_1_fc = create_feature_class(gdb_path, "Rows_1_pt", "POINT", sr_3857)
        rows_9_fc = create_feature_class(gdb_path, "Rows_9_pt", "POINT", sr_3857)

        create_feature_class(gdb_path, "EPSG_3857_pt", "POINT", sr_3857)
        create_feature_class(gdb_path, "EPSG_4283_pt", "POINT", sr_4283)
        create_feature_class(gdb_path, "EPSG_7856_pt", "POINT", sr_7856)

        create_feature_class(gdb_path, "ZM_NoZNoM_pt", "POINT", sr_3857)
        create_feature_class(gdb_path, "ZM_HasZ_pt", "POINT", sr_3857, has_z=True)
        create_feature_class(gdb_path, "ZM_HasM_pt", "POINT", sr_3857, has_m=True)
        create_feature_class(
            gdb_path,
            "ZM_HasZM_pt",
            "POINT",
            sr_3857,
            has_z=True,
            has_m=True
        )

        empty_state_fc = create_feature_class(gdb_path, "EmptyState_pt", "POINT", sr_3857)

        insert_point_rows(rows_1_fc, [(0, 0)])
        insert_point_rows(rows_9_fc, [(x, 0) for x in range(9)])
        create_empty_state_rows(empty_state_fc)

        validate_all(gdb_path)

    except arcpy.ExecuteError:
        log.error("ArcPy ExecuteError: program stopping")
        tb_text = traceback.format_exc()
        log.error(flatten_for_csv(tb_text))
        sys.exit(1)

    except Exception:
        log.error("Unhandled exception: program stopping")
        tb_text = traceback.format_exc()
        log.error(flatten_for_csv(tb_text))
        sys.exit(1)

    finally:
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        log.info(f"Finished")
        log.info(f"Duration          {duration}")
        logging.shutdown()


# program entry point when called from the command line
if __name__ == '__main__':
    setup_logger(log_folder)
    main()
