import numpy as np

# Configurations
SCREEN_WIDTH = 930              # width of the display
SCREEN_HEIGHT = 640             # height of the display
MSCALE = 100.0                  # scale of the display
MAX_FPS = 32                    # maximum frames per second
MAX_RANGE = 600                 # maximum range for reference
MAX_TIME = 300                  # maximum age of data (s)
SOFT_TIME = 150                 # soft age of data (s) (signal lost but might reappear)
BASE_LAT = 52.08409688522358    # latitude of the radar's base reference (Use Google Maps (right click on the map) to obtain Lat/lon coords of your choosing)
BASE_LON = 4.266612811234726    # longitude of the radar's base reference
F1SIZE = 14                    # Font size for large labels
F2SIZE = 10                    # Font size for small labels
FONT1 = r".\fonts\CONSOLA.TTF"  # path to the large font
FONT2 = r".\fonts\CONSOLAB.TTF"  # path to the small font
JSON_THROTTLE = 2               # frequency of JSON updates (s)
JSON_FILEPATH = r"\\192.168.2.3\LabDrive\barret\radar\aircraft.json"  # path to the JSON data file (change this to your dump1090 aircraft.json)

# Precompute trigonometric functions
BASE_LAT_RAD = np.radians(BASE_LAT)  # latitude of the radar's base in radians
BASE_LON_RAD = np.radians(BASE_LON)  # longitude of the radar's base in radians
COS_BASE_LAT = np.cos(BASE_LAT_RAD)  # cosine of the base latitude
SIN_BASE_LAT = np.sin(BASE_LAT_RAD)  # sine of the base latitude
