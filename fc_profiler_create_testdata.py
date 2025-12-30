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
    Writen for Python 3.11.11 as shipped with ArcGIS Pro 3.5.3

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
from arcpy.sa import * # pyright: ignore[reportMissingImports]
import logging
import os
import datetime
import sys
import traceback
from pathlib import Path    



log = logging.getLogger(__name__)

# -----------------------------------------
# run config
# -----------------------------------------
log_name = r"fc_profiler_testdata"
log_folder = r"."


# input parameters

# output parameters

# other config

# set the geoprocessing environment
arcpy.env.workspace = r'C:\Users\Mic\OneDrive\code\py_arcpy\fc_profiler_testdata' 
arcpy.env.overwriteOutput = True   # avoids having to test for existence and delete
arcpy.env.addOutputsToMap = False


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
        # do stuff here...

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