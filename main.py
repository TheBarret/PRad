import os
import time
import json
import pygame

from models import Craft
from functions import (color_lerp, show_traces, draw_spacer_rings)
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, 
                    MAX_TIME, SOFT_TIME, 
                    JSON_THROTTLE, JSON_FILEPATH, 
                    FONT1, FONT2, F1SIZE, F2SIZE, 
                    MAX_FPS, LX, LY, LS, FW, FH,
                    SCREEN_CX, SCREEN_CY)

# Initializers
AIRCRAFTS   = []                 # Array aircraft
HISTORY     = {}                 # Dict history (tracers)

def read_json():
    try:
        if os.path.isfile(JSON_FILEPATH):
            with open(JSON_FILEPATH, "r") as file:
                update_crafts(json.load(file))
        pygame.display.set_caption(f"PASSIVE RADAR - Detected {len(AIRCRAFTS)} crafts")
    except Exception as e:
        print(f"Error: {e}")


def update_crafts(data):
    global AIRCRAFTS
    for message in data.get("aircraft", []):
        # Validate message and update where possible
        if all(key in message for key in ["hex", "lat", "lon", "track"]):
            id, lat, lon, track = message["hex"], float(message["lat"]), float(message["lon"]), int(message["track"])
            craft = next((craft for craft in AIRCRAFTS if craft.id == id), None)
            if craft:
                craft.update_position(lat, lon, track)
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
                craft.updated = True
                save_craft_info(craft)
            else:
                craft = Craft(id, lat, lon)
                craft.updated = True
                AIRCRAFTS.append(craft)
                save_craft_info(craft)
        else:
            if "hex" in message and "lat" in message and "lon" in message:
                id, lat, lon = message["hex"], float(message["lat"]), float(message["lon"])
                craft = next((craft for craft in AIRCRAFTS if craft.id == id), None)
                if not craft:
                    craft = Craft(id, lat, lon)
                    craft.updated = True
                    AIRCRAFTS.append(craft)
                    save_craft_info(craft)

def save_craft_info(craft):
    craft_json = json.dumps(craft.__dict__)
    with open(f"./crafts/{craft.id}.json", 'w') as json_file:
        json_file.write(craft_json)

def render(surface, h1, h2):
    lx, ly = LX, LY     # craft plot offsets (see config)
    ls = LS             # craft plot spacing (see config)
    fw, fh = FW, FH     # craft plot width and height
    
    # Initialize total width of the stack
    length = 0  
    for i, craft in enumerate(sorted(AIRCRAFTS, key=lambda craft: craft.distance)):
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
            pygame.draw.rect(surface, (255, 255, 255), (fx, fy, fw, fh), 0)
            pygame.draw.rect(surface, (0, 0, 0), (fx, fy, fw, fh), 2)
        else:
            pygame.draw.rect(surface, (100, 100, 100), (fx, fy, fw, fh), 0)
            pygame.draw.rect(surface, (0, 0, 0), (fx, fy, fw, fh), 2)

        # Draw labels
        INF1 = h1.render(f"{craft.get_flight()}", True, (0, 0, 0))
        INF2 = h2.render(f"{int(craft.altitude)}ft {int(craft.speed)}Km/s {craft.cardinal}", True, (0, 0, 0))
        INF3 = h2.render(f"{int(craft.bearing)}° {int(craft.distance)}Km {craft.type}", True, (0, 0, 0))
        surface.blit(INF1, (fx + 10, fy + 5))
        surface.blit(INF2, (fx + 10, fy + 17))
        surface.blit(INF3, (fx + 10, fy + 24))

        # Draw blip
        draw_aircraft(surface, craft, h1, craft_stale)
        length += fw + ls    

# Draw craft position
def draw_aircraft(surface, craft, h1, stale, animation_offset=0):
    x, y = craft.position
    info = h1.render(f"{craft.get_flight()}", True, (255, 0, 0))
    surface.blit(info, (x - 25, y - 25))
    if not stale:
        # Draw animated ping
        if craft.animation_radius > 0:
            ping_color = color_lerp((127, 127, 127), (0, 255, 0), craft.rssi)
            pygame.draw.circle(surface, ping_color, (x, y), animation_offset + craft.animation_radius, 2)
    else:
        pygame.draw.rect(surface, (100, 100, 100), (x - 5, y - 5, 10, 10), 1)

def render_grid(surface, step=32, color=(50, 50, 50)):
    for y in range(0, SCREEN_HEIGHT + 1, step):
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y), 1)
    for x in range(0, SCREEN_WIDTH + 1, step):
        pygame.draw.line(surface, color, (x, 0), (x, SCREEN_HEIGHT), 1)

def update_older_sets(max_age):
    global AIRCRAFTS
    AIRCRAFTS = sorted(AIRCRAFTS, key=lambda craft: craft.age)
    current_time = time.time()
    index = 0
    while index < len(AIRCRAFTS) and current_time - AIRCRAFTS[index].age > max_age:
        index += 1
    AIRCRAFTS = AIRCRAFTS[index:]

def display_latency(surface, value, h1):
    label = h1.render(f"Latency: {value:.2f}ms", True, (255, 255, 255))
    surface.blit(label, (5, SCREEN_HEIGHT - 19))

def main():
    pygame.init()
    read_time = 0
    F1      = pygame.font.Font(FONT1, F1SIZE)
    F2      = pygame.font.Font(FONT2, F2SIZE)
    screen  = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock   = pygame.time.Clock()
    while True:
        latency = time.time()
        screen.fill((0, 0, 0))
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if current_time - read_time >= JSON_THROTTLE:
            update_older_sets(MAX_TIME)
            read_json()
            read_time = current_time

        show_traces(screen, HISTORY)
        render_grid(screen)
        draw_spacer_rings(screen,(SCREEN_CX,SCREEN_CY),150,5,25)
        render(screen, F1, F2)
        
        display_latency(screen, time.time() - latency, F1)
        pygame.display.flip()
        clock.tick(MAX_FPS)

if __name__ == "__main__":
    main()