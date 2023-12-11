import time
from config import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    MSCALE, 
    MOFFSET,
    BASE_LAT, 
    BASE_LON, 
    BASE_LAT_RAD, 
    BASE_LON_RAD, 
    COS_BASE_LAT, 
    SIN_BASE_LAT
)
from functions import (
    calculate_distance,
    calculate_relposition,
    calculate_bearing,
    calculate_cardinal,
    normalize_rssi,
    get_category_info,
    get_size_info,
)

class Craft:
    def __init__(self, id, lat, lon):
        self.id         = id
        self.seed       = int(str(id), 16)
        self.size       = 1
        self.speed      = 0
        self.rssi       = 0
        self.track      = 0
        self.altitude   = 0
        self.vert_rate  = 0
        self.maxcache   = 16
        self.altitude_m = 0
        self.speed_kmh  = 0
        self.category   = ""
        self.age        = time.time()
        self.type       = ""
        self.flight     = ""
        self.timestamps = []
        self.positions  = []
        self.altitudes  = []
        self.tracks     = []
        self.vrates     = []
        self.speeds     = []
        self.rssis      = []
        self.distances  = []
        self.animation_time = 0
        self.animation_rmax = 5
        self.animation_radius = 0
        self.animation_rev = False
        self.update(lat, lon)

    def update(self, lat, lon):
        self.age        = time.time()
        self.lat        = lat
        self.lon        = lon
        self.bearing    = calculate_bearing(lat, lon, BASE_LAT, BASE_LON, MOFFSET)
        self.cardinal   = calculate_cardinal(self.bearing)
        self.position   = calculate_relposition(lat, lon, BASE_LAT_RAD, BASE_LON_RAD, COS_BASE_LAT, SIN_BASE_LAT, SCREEN_WIDTH, SCREEN_HEIGHT, MSCALE)
        self.distance   = calculate_distance(BASE_LAT, BASE_LON, lat, lon, COS_BASE_LAT)
        self.positions.append(self.position)
        self.timestamps.append(time.time())
        self.distances.append(self.distance)
        self.trim_data(self.positions)
        self.trim_data(self.timestamps)
        self.trim_data(self.distances)

    def update_tracker(self, track):
        self.track = track
        self.tracks.append(track)
        self.trim_data(self.tracks)

    def update_altitude(self, altitude):
        self.altitude = altitude
        self.altitude_m = altitude * 0.3048    # 1 foot = 0.3048 meters
        self.altitudes.append(self.altitude)
        self.trim_data(self.altitudes)

    def update_vert_rate(self, vert_rate):
        self.vert_rate = vert_rate
        self.vrates.append(vert_rate)
        self.trim_data(self.vrates)

    def update_speed(self, speed):
        self.speed = speed
        self.speed_kmh = speed * 1.852        # 1 knot = 1.852 km/h
        self.speeds.append(speed)
        self.trim_data(self.speeds)

    def update_rssi(self, rssi, max_rssi=-10, min_rssi=-1):
        self.rssi = normalize_rssi(float(rssi), max_rssi, min_rssi)
        self.rssis.append(rssi)
        self.trim_data(self.rssis)

    def update_flight(self, flight):
        self.flight = flight
    
    def update_category(self, category):
        self.category = category
        self.size = get_size_info(category)
        self.type = get_category_info(category)

    def get_flight(self):
        return self.flight if self.flight else self.id.upper()

    def animate(self, modifier=0.03):
        rssi_norm = 10 - abs(self.rssi)
        self.animation_radius += rssi_norm * modifier * (1 if not self.animation_rev else -1)
        self.animation_rev = not self.animation_rev if self.animation_radius > self.animation_rmax or self.animation_radius <= 0 else self.animation_rev

    def trim_data(self, lst):
        if len(lst) > self.maxcache:
            lst = lst[-self.maxcache:]
