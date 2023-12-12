import os
import time
import json
import pygame
from transponder import (telemetry)
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, BASE_LAT, BASE_LON,
                    MAX_FPS, JSON_SOURCE, JSON_THROTTLE, MSCALE)

AIRCRAFTS   = []

# Fetch snapshot
def fetch_snapshot():
    try:
        if os.path.isfile(JSON_SOURCE):
            with open(JSON_SOURCE, "r") as file:
                data = json.load(file)
                update(data)
    except Exception as e:
        print(f"Error: {e}")

# Main updater
def update(data):
    global AIRCRAFTS
    pygame.display.set_caption(f"PASSIVE RADAR - Tracking {len(AIRCRAFTS)} transponders")
    for message in data.get("aircraft", []):
        # Update aircraft data
        if all(key in message for key in ["hex"]):
            icao = message["hex"]
            transponder = next((aircraft for aircraft in AIRCRAFTS if aircraft.ICAO == icao), None)
            if transponder:
                transponder.update(message)
            else:
                transponder = telemetry(icao, message)
                transponder.update(message)
                AIRCRAFTS.append(transponder)

# Main Render
def render(surface, h1, h2):
    for i, transponder in enumerate(sorted(AIRCRAFTS, key=lambda transponder: transponder.distance)):
        offset  = time.time() - transponder.age
        if offset <= JSON_THROTTLE and transponder.is_alive():
            transponder.draw_path(surface, 1)
            transponder.render(surface, h1, h2)

# Event handling
def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

# Main
def main():
    global GEOMAP
    pygame.init()
    rt      = 0
    H1      = pygame.font.Font(r".\fonts\CONSOLA.TTF", 12)
    H2      = pygame.font.Font(r".\fonts\CONSOLAB.TTF", 11)
    screen  = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock   = pygame.time.Clock()
    print("Starting PRad...")
    while True:
        current = time.time()
        screen.fill((0, 0, 0))

        check_events()
        if current - rt >= JSON_THROTTLE:
            fetch_snapshot()
            rt = current

        render(screen, H1, H2)

        pygame.display.flip()
        clock.tick(MAX_FPS)

if __name__ == "__main__":
    main()