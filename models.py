import time
from config import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    MSCALE, 
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
    color_lerp,
    normalize_rssi,
    get_category_info,
    get_size_info,
)

class Craft:
    def __init__(self, id, lat, lon):
        self.id = id
        self.size = 1
        self.speed = 0
        self.rssi = 0.5
        self.track = 0
        self.altitude = 0
        self.vert_rate = 0
        self.maxcache = 64
        self.updated = False
        self.category = ""
        self.age = time.time()
        self.type = ""
        self.flight = ""
        self.positions = []
        self.altitudes = []
        self.animation_time = 0
        self.animation_rmax = 10
        self.animation_radius = 0
        self.animation_rev = False
        self.update_position(lat, lon, 0)
    def update_flight(self, flight):
        self.flight = flight
    def update_tracker(self, track):
        self.track = track
    def update_altitude(self, altitude):
        self.altitude = altitude
        self.altitudes.append(self.altitude)
        if len(self.altitudes) > self.maxcache:
            self.altitudes = self.altitudes[-self.maxcache:]
    def update_category(self, category):
        self.category = category
        self.size = get_size_info(category)
        self.type = get_category_info(category)
    def update_vert_rate(self, vert_rate):
        self.vert_rate = vert_rate
    def update_speed(self, speed):
        self.speed = speed
    def update_rssi(self, rssi, max_rssi=-10,min_rssi=-1):
        self.rssi = normalize_rssi(float(rssi),max_rssi, min_rssi)
    def update_position(self, lat, lon, track):
        self.age = time.time()
        self.lat = lat
        self.lon = lon
        self.track = track
        self.bearing = calculate_bearing(lat, lon, BASE_LAT, BASE_LON)
        self.cardinal = calculate_cardinal(self.bearing)
        self.position = calculate_relposition(lat, lon, BASE_LAT_RAD, BASE_LON_RAD, COS_BASE_LAT, SIN_BASE_LAT, SCREEN_WIDTH, SCREEN_HEIGHT, MSCALE)
        self.distance = calculate_distance(BASE_LAT, BASE_LON, lat, lon, COS_BASE_LAT)
        self.store_position(self.position)
    def store_position(self, position):
        self.positions.append(position)
        if len(self.positions) > self.maxcache:
            self.positions = self.positions[-self.maxcache:]
    def get_flight(self):
        if len(self.flight) > 0:
            return self.flight
        else:
            return self.id.upper()
    def animate(self, modifier=0.02):
        rssi_norm = 10 - abs(self.rssi)
        if not self.animation_rev:
            self.animation_radius += rssi_norm * modifier
        else:
            self.animation_radius -= rssi_norm * modifier
        if self.animation_radius > self.animation_rmax:
            self.animation_rev = not self.animation_rev
        elif self.animation_radius <= 0:
            self.animation_rev = not self.animation_rev
