from skyfield.api import Topos, load, EarthSatellite
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Load timescale and TLE data
ts = load.timescale()
satellites = load.tle_file('https://celestrak.com/NORAD/elements/stations.txt')
satellite = {sat.name: sat for sat in satellites}['ISS (ZARYA)']  # for example, using the ISS

satellite = EarthSatellite(
    '1 42525U 18016A   23283.11958293  .00000000  00000-0  0  9996',
    '2 42525  0.0000   0.0000 0000000  0.0000  0.0000 14.98088827356309'
)

satellite = EarthSatellite(
    '1 41987U 17023A   23283.18765165  .00000000  00000-0  0  9996',
    '2 41987  0.0000   0.0000 0000000  0.0000  0.0000 14.98079142412921'
)

# Define the observer's location
latitude, longitude = 40.0, -74.0  # example: New York City
observer_location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

# Set the time range to analyze (e.g., the next 24 hours)
t_start = ts.now()
t_end = ts.now() + timedelta(days=1)

# Define the step size in seconds (to make calculations faster)
step_size_seconds = 60

# Generate time points for plotting ground track
times = []
positions = []

# Time loop to check if the satellite is within a close distance to the observer
t = t_start
passes = []
while t < t_end:
    times.append(t)
    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()
    positions.append((subpoint.latitude.degrees, subpoint.longitude.degrees))

    difference = satellite - observer_location
    topocentric = difference.at(t)
    alt, az, distance = topocentric.altaz()

    # Check if the satellite is "above" the horizon
    if alt.degrees > 0:
        passes.append((t.utc_datetime(), alt.degrees))

    # Increment time by the step size
    t = t.utc_datetime() + timedelta(seconds=step_size_seconds)
    t = ts.utc(t)

# Display the passes (date, altitude in degrees)
for pass_time, altitude in passes:
    print(f"Time: {pass_time}, Altitude: {altitude:.2f} degrees")

# Convert positions to numpy array for easier indexing
positions = np.array(positions)
lats, lons = positions[:, 0], positions[:, 1]

# Plotting the ground track and observer location
fig, ax = plt.subplots(figsize=(12, 8))

# Use Basemap to create a world map projection
m = Basemap(projection='mill', resolution='l', ax=ax)
m.drawcoastlines()
m.drawcountries()
m.drawparallels(np.arange(-90, 90, 30), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180, 180, 60), labels=[0, 0, 0, 1])

# Convert satellite lat/lon to map coordinates and plot the ground track
x, y = m(lons, lats)
m.plot(x, y, 'b-', label='Satellite Ground Track', linewidth=1)

# Plot observer location
obs_x, obs_y = m(longitude, latitude)
m.plot(obs_x, obs_y, 'ro', markersize=8, label='Observer Location')

# Highlight passes when satellite is near the observer
threshold_distance = 10000  # Distance in km for "near pass"
passes = []

near_pass_legend = False

for i, time in enumerate(times):
    geocentric = satellite.at(time)
    difference = (satellite - observer_location).at(time)
    distance_km = difference.distance().km
    if distance_km < threshold_distance:
        passes.append((lats[i], lons[i]))
        # Mark the "near pass" location on the map
        pass_x, pass_y = m(lons[i], lats[i])
        if not near_pass_legend:
            near_pass_legend = True
            m.plot(pass_x, pass_y, 'go', markersize=6, label='Near Pass')  # Green dot for each pass
        else:
            m.plot(pass_x, pass_y, 'go', markersize=6)  # Green dot for each pass

# Add legend and title
plt.legend(loc='upper left')
plt.title(f'Satellite Ground Track and Passes Over ({latitude}, {longitude})')
plt.show()
