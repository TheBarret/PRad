import numpy as np

def color_lerp(color1, color2, value):
    c1 = np.array([color1[0], color1[1], color1[2]])
    c2 = np.array([color2[0], color2[1], color2[2]])
    values = np.array([value])
    color_diff = c2 - c1
    return c1 + values * color_diff

def normalize_rssi(rssi, min_value=-10, max_value=-1):
    if min_value == max_value:
        return 0.5
    norm_value = (rssi - min_value) / (max_value - min_value)
    norm_value = np.clip(norm_value, 0, 1)
    return norm_value

def mercator_difference(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return np.sqrt(dx**2 + dy**2)

def mercator_to_coords(x, y, SCREEN_WIDTH, SCREEN_HEIGHT, sfactor=100.0):
    radar_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) / 2
    scale = radar_radius / sfactor
    x = (x - radar_radius) / scale
    y = (y - radar_radius) / scale
    R = 6371
    lat_rad = 2 * np.arctan(np.exp(y / R)) - np.pi / 2
    lon_rad = (x / R) * np.pi
    lat = np.degrees(lat_rad)
    lon = np.degrees(lon_rad)
    return lat, lon

def calculate_distance(lat1, lon1, lat2, lon2, COS_BASE_LAT):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + COS_BASE_LAT * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance

def calculate_distance_simple(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = np.radians([lat1, lon1, lat2, lon2])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    # Haversine formula
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance

def calculate_relposition(lat, lon, BASE_LAT_RAD, BASE_LON_RAD, COS_BASE_LAT, SIN_BASE_LAT, SCREEN_WIDTH, SCREEN_HEIGHT, sfactor=100.0):
    delta_lat = np.radians(lat - np.degrees(BASE_LAT_RAD))
    delta_lon = np.radians(lon - np.degrees(BASE_LON_RAD))
    R = 6371
    a = np.sin(delta_lat / 2) ** 2 + COS_BASE_LAT * np.cos(np.radians(lat)) * np.sin(delta_lon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    y = np.sin(delta_lon) * COS_BASE_LAT
    x = np.cos(BASE_LAT_RAD) * np.sin(np.radians(lat)) - SIN_BASE_LAT * np.cos(np.radians(lat)) * np.cos(delta_lon)
    bearing = np.arctan2(y, x)
    radar_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) / 2
    scale = radar_radius / sfactor
    x = radar_radius + distance * scale * np.cos(bearing)
    y = radar_radius + distance * scale * np.sin(bearing)
    return x, y

def calculate_mercposition(lat, lon, BASE_LAT, BASE_LON, SCREEN_WIDTH, SCREEN_HEIGHT, sfactor=100.0):
    R = 6371
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    base_lat_rad = np.radians(BASE_LAT)
    base_lon_rad = np.radians(BASE_LON)
    x = R * (lon_rad - base_lon_rad)
    y = R * np.log(np.tan(np.pi / 4 + lat_rad / 2) / np.tan(np.pi / 4 + base_lat_rad / 2))
    scale = SCREEN_WIDTH / (2 * np.pi * R) * sfactor
    x = SCREEN_WIDTH / 2 + x * scale
    y = SCREEN_HEIGHT / 2 - y * scale 
    return x, y

def calculate_bearing(lat, lon, BASE_LAT_RAD, BASE_LON, OFFSET=0):
    bearing = calculate_bearing_offset(BASE_LAT_RAD, BASE_LON, lat, lon, OFFSET)
    return bearing

def calculate_bearing_offset(lat1, lon1, lat2, lon2, offset=0):
    delta_lon = np.radians(lon2 - lon1)
    y = np.sin(delta_lon)
    x = np.cos(np.radians(lat2)) * np.sin(np.radians(lat2 - lat1))
    bearing = (np.degrees(np.arctan2(y, x)) + 360) % 360
    return (bearing + offset) % 360

def calculate_cardinal(bearing):
    cardinals = ["N", "N-NE", "N-E", "E-NE", "E", "E-SE", "S-E", "S-SE", "S", "S-SW", "S-W", "W-SW", "W", "W-NW", "N-W", "N-NW"]
    index = round(bearing / 22.5) % 16
    return cardinals[index]

def get_size(category):
    if category == "A0":
        return 10
