import sys
import platform
import importlib.util

print("Python EXE     : " + sys.executable)
print("Version        : " + sys.version)
print("Architecture   : " + platform.architecture()[0])

# Modern replacement for imp.find_module
spec = importlib.util.find_spec("arcpy")
if spec and spec.origin:
    print("Path to arcpy  : " + spec.origin)
else:
    print("Path to arcpy  : Not Found")