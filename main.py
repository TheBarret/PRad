import os
import time
import json
import pygame
import numpy as np

from collections import defaultdict
from models import Craft
from functions import (color_lerp, normalize_rssi, draw_spacer_rings)
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, 
                    MAX_TIME, SOFT_TIME, 
                    JSON_THROTTLE, JSON_FILEPATH, 
                    FONT1, FONT2, F1SIZE, F2SIZE, 
                    MAX_FPS, LX, LY, LS, FW, FH,
                    SCREEN_CX, SCREEN_CY)

# Initializers
AIRCRAFTS   = []                 # Array aircraft
HISTORY     = {}                 # Dict history
JSON_THROTTLE_2 = JSON_THROTTLE * 2
HM_MAP  = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] # Thresholds map for rssi ranges
HM_STEP = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] # Step values for each threshold

def read_json():
    try:
        if os.path.isfile(JSON_FILEPATH):
            with open(JSON_FILEPATH, "r") as file:
                update_crafts(json.load(file))
        pygame.display.set_caption(f"PASSIVE RADAR - Live: {len(AIRCRAFTS)} Database: {len(HISTORY)}")
    except Exception as e:
        print(f"Error: {e}")

def load_history(folder="./crafts/"):
    global HISTORY
    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            ref = os.path.join(folder, file_name)
            id = file_name.split(".")[0]
            if not id in HISTORY:
                with open(ref, "r") as file:
                    cdata = json.load(file)
                    HISTORY[id] = cdata

def update_crafts(data):
    global AIRCRAFTS
    for message in data.get("aircraft", []):
        # Validate message and update
        if all(key in message for key in ["hex", "lat", "lon"]):
            id, lat, lon = message["hex"], float(message["lat"]), float(message["lon"])
            craft = next((craft for craft in AIRCRAFTS if craft.id == id), None)
            if craft:
                # Update where available
                craft.update(lat, lon)
                if "flight" in message:
                    craft.update_flight(message["flight"])
                if "altitude" in message:
                    craft.update_altitude(float(message["altitude"]))
                if "category" in message:
                    craft.update_category(message["category"])
                if "vert_rate" in message:
                    craft.update_vert_rate(float(message["vert_rate"]))
                if "speed" in message:
                    craft.update_speed(float(message["speed"]))
                if "rssi" in message:
                    craft.update_rssi(float(message["rssi"]))
                if "track" in message:
                    craft.update_tracker(int(message["track"]))
                save_craft_info(craft)
            else:
                craft = Craft(id, lat, lon)
                AIRCRAFTS.append(craft)
                save_craft_info(craft)
        else:
            if "hex" in message and "lat" in message and "lon" in message:
                id, lat, lon = message["hex"], float(message["lat"]), float(message["lon"])
                craft = next((craft for craft in AIRCRAFTS if craft.id == id), None)
                if not craft:
                    craft = Craft(id, lat, lon)
                    AIRCRAFTS.append(craft)
                    save_craft_info(craft)

def save_craft_info(craft):
    craft_json = json.dumps(craft.__dict__)
    with open(f"./crafts/{craft.id}.json", 'w') as json_file:
        json_file.write(craft_json)

def render(surface, h1, h2, metric=True):
    length = 0          # length offset
    lx, ly = LX, LY     # craft plot offsets (see config)
    ls = LS             # craft plot spacing (see config)
    fw, fh = FW, FH     # craft plot width and height

    for i, craft in enumerate(sorted(AIRCRAFTS, key=lambda craft: craft.seed)):
        craft_stale = False
        current_time = time.time()
        ttl = current_time - craft.age
        if ttl >= SOFT_TIME:
            craft_stale = True
        # Update horizontal offsets
        fx = lx + length 
        fy = ly + (fh + ls) * (i // (SCREEN_WIDTH // (fw + ls)))
        if length + fw > SCREEN_WIDTH:
            length = 0
            fx = 0
        # Draw rectangle
        if not craft_stale:
            craft.animate()
            if craft.distance <= 1:
                pygame.draw.rect(surface, (0, 255, 0), (fx, fy, fw, fh), 0)
                pygame.draw.rect(surface, (0, 0, 0), (fx, fy, fw, fh), 2)
            else:
                pygame.draw.rect(surface, (255, 255, 255), (fx, fy, fw, fh), 0)
                pygame.draw.rect(surface, (0, 0, 0), (fx, fy, fw, fh), 2)
        else:
            pygame.draw.rect(surface, (100, 100, 100), (fx, fy, fw, fh), 0)
            pygame.draw.rect(surface, (0, 0, 0), (fx, fy, fw, fh), 2)
        # Draw labels
        draw_aircraft_labels(surface, craft, h1, h2, fx, fy, metric)
        # Draw blip
        draw_aircraft(surface, craft, h1, craft_stale)
        # Increase length offset
        length += fw + ls    

# Draw craft position
def draw_aircraft(surface, craft, h1, stale, animation_offset=0):
    x, y = craft.position
    info = h1.render(f"{craft.get_flight()}", True, (255, 0, 0))
    surface.blit(info, (x - 25, y - 25))
    if not stale:
        # Draw animated ping
        if craft.animation_radius > 0:
            pygame.draw.circle(surface, (0, 255, 0), (x, y), animation_offset + craft.animation_radius, 2)
    else:
        pygame.draw.rect(surface, (100, 100, 100), (x - 5, y - 5, 10, 10), 1)

def draw_aircraft_labels(surface, craft, h1, h2, fx, fy, metric):
    if not metric:
        INF1 = h1.render(f"{craft.get_flight()}", True, (0, 0, 0))
        INF2 = h2.render(f"{int(craft.altitude)}ft {int(craft.speed)}kt {craft.cardinal}", True, (0, 0, 0))
        INF3 = h2.render(f"{int(craft.bearing)}° {int(craft.distance)}Km {craft.type}", True, (0, 0, 0))
    else:
        INF1 = h1.render(f"{craft.get_flight()}", True, (0, 0, 0))
        INF2 = h2.render(f"{int(craft.altitude_m)}m {int(craft.speed_kmh)}km/h {craft.cardinal}", True, (0, 0, 0))
        INF3 = h2.render(f"{int(craft.bearing)}° {int(craft.distance)}Km {craft.type}", True, (0, 0, 0))

        surface.blit(INF1, (fx + 10, fy + 5))
        surface.blit(INF2, (fx + 10, fy + 17))
        surface.blit(INF3, (fx + 10, fy + 24))

def draw_heatmap(surface, f1, grid_size=32, verbose=False):
    global HISTORY, HM_MAP, HM_STEP
    if len(HISTORY) < 1: return
    heatmap = defaultdict(float)
    upositions = set()
    for id, data in HISTORY.items():
        positions = np.array(data['positions'])
        rssis = np.array(data['rssis'])
        # Normalize RSSI values
        normalized_rssis = normalize_rssi(rssis)
        # Calculate and cast positions
        xv = (positions[:, 0] // grid_size).astype(int)
        yv = (positions[:, 1] // grid_size).astype(int)
        upositions.update(zip(xv, yv))
        for (x, y), r in zip(zip(xv, yv), normalized_rssis):
            for threshold, weight in zip(HM_MAP, HM_STEP):
                if r <= threshold:
                    heatmap[(x, y)] += weight
                    break
    for (x, y) in upositions:
        rssi_sum = heatmap[(x, y)]
        rssi_avg = min(1, max(0, (rssi_sum / len(HISTORY))))
        color = color_lerp((0, 0, 90), (0, 0, 255), rssi_avg)
        pygame.draw.rect(surface, color, (x * grid_size, y * grid_size, grid_size, grid_size), 0)
        if verbose:
            tag = f1.render(f'{rssi_avg:.2f}', True, (90, 90, 90))
            surface.blit(tag, (x * grid_size, y * grid_size))

def render_grid(surface, step=32, color=(50, 50, 50)):
    for y in range(0, SCREEN_HEIGHT + 1, step):
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y), 1)
    for x in range(0, SCREEN_WIDTH + 1, step):
        pygame.draw.line(surface, color, (x, 0), (x, SCREEN_HEIGHT), 1)

def remove_stale(max_age):
    global AIRCRAFTS
    AIRCRAFTS = sorted(AIRCRAFTS, key=lambda craft: craft.age)
    current_time = time.time()
    index = 0
    while index < len(AIRCRAFTS) and current_time - AIRCRAFTS[index].age > max_age:
        index += 1
    AIRCRAFTS = AIRCRAFTS[index:]

def display_latency(surface, value, h1):
    label = h1.render(f"Latency: {value:.4f}ms", True, (255, 255, 255))
    surface.blit(label, (5, SCREEN_HEIGHT - 19))

def main():
    pygame.init()
    read_time   = 0
    write_time  = 0
    F1          = pygame.font.Font(FONT1, F1SIZE)
    F2          = pygame.font.Font(FONT2, F2SIZE)
    screen      = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock       = pygame.time.Clock()

    # Cache history data for heatmap


    while True:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if current_time - read_time >= JSON_THROTTLE:
            remove_stale(MAX_TIME)
            read_json()
            read_time = current_time
        if current_time - write_time >= JSON_THROTTLE_2:
            load_history()
            write_time = current_time

        screen.fill((0, 0, 0))

        draw_heatmap(screen, F2)
        render_grid(screen)

        draw_spacer_rings(screen,(SCREEN_CX - 25,SCREEN_CY - 25),50,8,50)
        render(screen, F1, F2)
        
        display_latency(screen, time.time() - current_time, F1)
        pygame.display.flip()
        clock.tick(MAX_FPS)

if __name__ == "__main__":
    main()