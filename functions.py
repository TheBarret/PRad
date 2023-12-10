import os
import math
import json
import pygame
import numpy as np

SIZES = { # size of each aircraft category
    'A0': 3,
    'A1': 3,
    'A2': 4,
    'A3': 5,
    'A4': 4,
    'A5': 4,
    'A6': 4,
    'A7': 3,
    'A8': 3,
    'A9': 2,
    'DEFAULT': 1
}
DESC = { # description of each aircraft category
    'A0': 'Exempt',
    'A1': 'Light',
    'A2': 'Small',
    'A3': 'Large',
    'A4': 'HPerf',
    'A5': 'Sonic',
    'A6': 'L.craft',
    'A7': 'Glider/Rotor',
    'A8': 'UAS/UAV',
    'A9': 'RC/DRONE',
    'DEFAULT': 'Undefined'
}

def show_trace(surface, craft, tint=(124, 252, 0), folder="./crafts/"):
    craft_id = craft.id
    file_path = f"{folder}{craft_id}.json"
    if os.path.isfile(file_path):
        with open(file_path, "r") as file:
            craft_data = json.load(file)
        if "history" in craft_data:
            history = craft_data["history"]
            if len(history) > 1:
                history_points = [
                    (
                        int(point[0]),
                        int(point[1])
                    ) for point in history
                ]
                pygame.draw.lines(surface, tint, False, history_points, 1)

def show_traces(surface, history, tint=(124, 252, 0), folder="./crafts/"):
    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder, file_name)
            if file_path in history:
                craft_data = history[file_path]
            else:
                with open(file_path, "r") as file:
                    craft_data = json.load(file)
                    history[file_path] = craft_data
            if "positions" in craft_data:
                craft_positions = craft_data["positions"]
                if len(craft_positions) > 1:
                    history_points = [(int(point[0]), int(point[1])) for point in craft_positions]
                    pygame.draw.lines(surface, tint, False, history_points, 2)

def draw_heading_line(surface, craft):
    if len(craft.history) < 2:
        return
    center_x, center_y = craft.position
    start_x, start_y = craft.history[0]
    end_x, end_y = craft.history[-1]
    angle = math.atan2(end_y - start_y, end_x - start_x)
    line_end_x = center_x + craft.size * math.cos(angle)
    line_end_y = center_y + craft.size * math.sin(angle)
    pygame.draw.line(surface, (124, 252, 0), (center_x, center_y), (line_end_x, line_end_y), 1)

def get_category_info(category):
    global DESC
    description = DESC.get(category, None)
    return description

def get_size_info(category):
    global SIZES
    size = SIZES.get(category, 0)
    return size

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

def calculate_distance(lat1, lon1, lat2, lon2, COS_BASE_LAT):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + COS_BASE_LAT * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
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

def calculate_bearing(lat, lon, BASE_LAT_RAD, BASE_LON):
    bearing = calculate_bearing_offset(BASE_LAT_RAD, BASE_LON, lat, lon, 0)
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