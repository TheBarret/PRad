import numpy as np

# Configurations
SCREEN_WIDTH    = 1024                   # width of the display
SCREEN_HEIGHT   = 800                   # height of the display
MAX_FPS         = 30                    # maximum frames per second (Default: 30)
MAX_RANGE       = 600                   # maximum range for reference (Default: 300)  
MAX_TIME        = 150                   # maximum age of data (s)
MSCALE          = 80                    # Position scale
BASE_LAT        = 52.3081 #52.08409688522358     # latitude of the radar's base reference
BASE_LON        = 4.7649  #4.266612811234726     # longitude of the radar's base reference

JSON_THROTTLE   = 2
JSON_SOURCE     = r"\\192.168.2.3\LabDrive\barret\radar\aircraft.json"  

# Precompute trigonometric functions
BASE_LAT_RAD = np.radians(BASE_LAT)  # latitude of the radar's base in radians
BASE_LON_RAD = np.radians(BASE_LON)  # longitude of the radar's base in radians
COS_BASE_LAT = np.cos(BASE_LAT_RAD)  # cosine of the base latitude
SIN_BASE_LAT = np.sin(BASE_LAT_RAD)  # sine of the base latitude