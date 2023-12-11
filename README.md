# PRad - Passive Radar Interface

Status: VERY ALPHA, UNFINISHED

Requirements:
- A linux shell (VM or NAS)
- RTL-SDR Device
- Dump1090 (fa/mu versions)



Versions:

![afbeelding](https://github.com/TheBarret/PRad/assets/25234371/b9ec96ac-a704-4fc2-a5cc-ecfda63706d9)



## Usage

To set up PRad with `dump1090` (compatible with mutability and fa), use the following command line:

```bash
dump1090-mutability --device-index 0 --gain 49.6 --enable-agc \
                    --lat 52.18409688522358 --lon 4.166612811234726 --max-range 300 \
                    --fix --metric --modeac --gnss \
                    --write-json ./ --write-json-every 2 --json-location-accuracy 1 \
                    --quiet
```

### dump1090 Parameters Explained:
```
- device-index 0:
  Specifies the index of the device to use. 0 indicates the first available device.

- gain 49.6:
  Sets the RTL-SDR dongle gain to 49.6 dB, optimizing reception based on signal strength.

- enable-agc:
  Enables Automatic Gain Control (AGC) for dynamic gain adjustment based on signal conditions.

- lat 52.18409688522358 --lon 4.166612811234726:
  Sets receiver's latitude and longitude for accurate aircraft positioning on the map.

- max-range 300:
  Defines the maximum range for aircraft tracking, limiting reception to 300 nautical miles.

- fix:
  Enables position-fixing information usage, improving aircraft position accuracy.

- metric:
  Specifies the metric system for measurements (e.g., distance in kilometers).

- modeac:
  Activates decoding of Mode A/C transponder information, providing additional aircraft details.

- gnss:
  Enables decoding of GNSS (Global Navigation Satellite System) information, improving location accuracy.

- write-json ./ --write-json-every 2 --json-location-accuracy 1:
  Configures writing JSON files with aircraft information every 2 seconds, with location accuracy set to 1 meter.

- quiet:
  Runs dump1090 in quiet mode, reducing console output.
```
This setup produces JSON data every 2 seconds, suitable for network drives or APIs/web scripts for data retrieval. 
