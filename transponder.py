import os
import json
import time
import pygame
import numpy as np
from config import (SCREEN_WIDTH, 
                    SCREEN_HEIGHT, 
                    MSCALE,
                    BASE_LAT, 
                    BASE_LON, 
                    BASE_LAT_RAD, 
                    BASE_LON_RAD, 
                    COS_BASE_LAT, 
                    SIN_BASE_LAT)

from functions import (calculate_distance,
                       mercator_difference,
                       calculate_relposition,
                       calculate_mercposition,
                       calculate_bearing,
                       calculate_cardinal,
                       normalize_rssi,
                       color_lerp)

class telemetry:
    def __init__(self, hex, message):
        self.ICAO       = hex           # ICAO (24-bit) hexadecimal
        self.squawk     = "0"           # ATC Identification
        self.flight     = "0"           # Flight name
        self.lat        = 0             # Latitude
        self.lon        = 0             # Longitude
        self.age        = 0             # Age of data (s)
        self.rssi       = 0             # Rssi (dBm)
        self.offset     = -90           # Coordinates angle offset (degrees)
        self.max_age    = 300           # Age of stale data (s)
        self.size       = 10            # Size
        self.size_h     = self.size // 2# Size / 2 
        self.bearing    = 0             # Bearing (degrees)
        self.rpos       = (0, 0)        # Relative position
        self.mpos       = (0, 0)        # Mercator position
        self.vrate      = 0             # Vrates (ft/s)
        self.cardinal   = "*"           # Cardinal reference
        self.category   = "*"          # Category of craft
        self.distance   = 0             # Distance (unit depends on dump1090 configuration)
        self.altitude   = 0             # Altitude (ft)
        self.altitude_m = 0             # Altitude (m)
        self.speed      = 0             # Speed (nm/h)
        self.speed_kmh  = 0             # Speed (km/h)
        self.track      = 0             # Track (degrees)
        self.temp       = r".\cache"    # Temporary cache directory
        self.timestamps = []            # Time stamp series
        self.positions  = []            # Positions series (mercator projection)
        self.altitudes  = []            # Altitudes series (ft)
        self.tracks     = []            # Tracks series (heading degrees)
        self.speeds     = []            # Speeds series (kt)
        self.vrates     = []            # Vrates series (ft/s)
        self.rssis      = []            # Rssi series (dBm)
        self.backlog    = 32            # Maximum dataset history length
        self.Foreground = (255,255,255) # Foreground color
        self.background = (0  ,0  ,0  ) # Background color
        self.border     = (100,100,100) # Border color
        self.update(message)
        
    def update(self, message):
        if "squawk"     in message: self.squawk     = message["squawk"]
        if "flight"     in message: self.flight     = message["flight"].strip()
        if "lat"        in message: self.lat        = message["lat"]
        if "lon"        in message: self.lon        = message["lon"]
        if "category"   in message: self.category   = message["category"]
        if "vert_rate"  in message: self.update_vrate(message["vert_rate"])
        if "track"      in message: self.update_tracker(message["track"])
        if "altitude"   in message: self.update_altitude(message["altitude"])
        if "speed"      in message: self.update_speed(message["speed"])
        if "rssi"       in message: self.update_rssi(message["rssi"])
        if self.lat + self.lon > 0:
            self.bearing    = calculate_bearing(self.lat, self.lon, BASE_LAT, BASE_LON, self.offset)
            self.cardinal   = calculate_cardinal(self.track)
            self.rpos       = calculate_relposition(self.lat, self.lon, BASE_LAT_RAD, BASE_LON_RAD, 
                                                    COS_BASE_LAT, SIN_BASE_LAT, SCREEN_WIDTH, SCREEN_HEIGHT, MSCALE)
            self.mpos       = calculate_mercposition(self.lat, self.lon, BASE_LAT, BASE_LON, SCREEN_WIDTH, SCREEN_HEIGHT, MSCALE)
            self.distance   = calculate_distance(BASE_LAT, BASE_LON, self.lat, self.lon, COS_BASE_LAT)
            if not self.positions: 
                self.positions.append(self.mpos)
            self.update_timestamp()
            self.update_position()
            self.save()

    def update_position(self, threshold=5):
        if not self.positions or self.mpos != self.positions[-1]:
            if self.positions:  # Check if empty
                x1, y1 = self.positions[-1]
                x2, y2 = self.mpos
                offset = mercator_difference(x1, y1, x2, y2)
                if offset >= threshold:
                    self.positions.append(self.mpos)
        self.trim(self.positions)

    def update_timestamp(self):
        self.timestamps.append(time.time())
        self.trim(self.timestamps)

    def update_tracker(self, track):
        self.track = track
        self.tracks.append(track)
        self.trim(self.tracks)   

    def update_altitude(self, altitude):
        self.altitude = altitude
        self.altitude_m = altitude * 0.3048    # 1 foot = 0.3048 meters
        self.altitudes.append(self.altitude)
        self.trim(self.altitudes)

    def update_vrate(self, vrate):
        self.vrate = vrate
        self.vrates.append(vrate)
        self.trim(self.vrates)

    def update_speed(self, speed):
        self.speed = speed
        self.speed_kmh = speed * 1.852        # 1 knot = 1.852 km/h
        self.speeds.append(speed)
        self.trim(self.speeds)

    def update_rssi(self, rssi, threshold=50):
        self.rssi = min(50, normalize_rssi(abs(rssi),0,threshold))
        self.rssis.append(self.rssi)
        self.trim(self.rssis)

    def save(self):
        data = json.dumps(self.__dict__)
        self.age = time.time()
        with open(os.path.join(self.temp, f"{self.ICAO}.json"), 'w') as file:
            file.write(data)

    def is_alive(self):
        return time.time() - self.age < self.max_age
    
    def draw_path(self, surface, scale=1, markers=1):
        history = self.get_path_history(scale)
        if self.rssi and len(history) >= 2:
            tint = color_lerp((255,0,0), (0,255,0), self.rssi)
            pygame.draw.lines(surface, tint, False, history, 1)
            for point in history:
                pygame.draw.rect(surface, (0, 255, 0), (int(point[0])-1, int(point[1])-1, 2, 2), markers)

    def get_path_history(self, scale=1):
        return [(int(x * scale), int(y * scale)) for x, y in self.positions]
    
    def get_rssi_history(self):
        return [(normalize_rssi(float(i))) for i in self.rssis]

    def trim(self, data):
        if len(data) > self.backlog:
            data = data[-self.backlog:]

    def get_status(self):
        if self.vrate < 0:
            return "↓"
        elif self.vrate == 0:
            return ""
        else:
            return "↑"
        
    def get_tag(self):
        if len(self.flight) > 0:
            return self.flight
        else:
            return self.ICAO.upper()
        
    def render(self, surface, h1, h2):
        x, y = self.mpos
        altp = (self.altitude - 500) / (50000 - 500)
        if self.altitude is not None:
            color = (int((1 - altp) * 255), int(altp * 255), 0)
        else:
            color = (255, 255, 255)
        if self.category == "*":
            tag  = h1.render(f"[{self.ICAO.upper()}]", True, self.Foreground)
            surface.blit(tag, (x - 25, y - 30))
        else:
            tag  = h1.render(f"[{self.category}-{self.get_tag()}{self.get_status()}]", True, color)
            surface.blit(tag, (x - 50, y - 30))
            if self.altitude >= 30000:
                info = h2.render(f"ALT {int(self.altitude_m)//1000}Km ~ {int(self.distance)}Km", True, self.Foreground)
                surface.blit(info, (x - 50, y - 20))
        self.render_airplane(surface, self.size, self.track, (x, y), color)

    def render_airplane(self, surface, size, angle, mpos, tint, offset=-180):
        x, y = mpos
        angle += offset
        airplane_points_local = np.array([
                    [0, -size * 0.1],           # Nose
                    [-size * 0.7, -size * 0.7], # Top left
                    [0, size],                  # Tail
                    [size * 0.7, -size * 0.7],  # Top right
        ])
        rotation_matrix = np.array([
            [np.cos(np.radians(angle)), -np.sin(np.radians(angle))],
            [np.sin(np.radians(angle)), np.cos(np.radians(angle))]
        ])
        airplane_points_rotated = np.dot(airplane_points_local, rotation_matrix.T)
        airplane_points_translated = airplane_points_rotated + np.array([x, y])
        pygame.draw.polygon(surface, tint, airplane_points_translated, 0)