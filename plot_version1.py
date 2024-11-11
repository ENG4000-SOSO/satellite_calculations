from skyfield.api import Topos, load, EarthSatellite
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap

THRESHOLD_DISTANCE_KM = 1000

ts = load.timescale()

# satellite = EarthSatellite(
#     '1 00001U          23274.66666667  .00000000  00000-0  00000-0 0 00001',
#     '2 00001 097.3597 167.6789 0009456 299.5645 340.3650 15.25701051000010'
# )
satellites = load.tle_file('https://celestrak.com/NORAD/elements/stations.txt')
satellite = {sat.name: sat for sat in satellites}['ISS (ZARYA)']  # for example, using the ISS

ground_station_latitude, ground_station_longitude = 40.0, -74.0
observer_location = Topos(latitude_degrees=ground_station_latitude, longitude_degrees=ground_station_longitude)

t_start = ts.now()
t_end = ts.now() + timedelta(days=1)

lats = []
lons = []

pass_lats = []
pass_lons = []

t = t_start
while t < t_end:

    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()

    lats.append(subpoint.latitude.degrees)
    lons.append(subpoint.longitude.degrees)

    difference = (satellite - observer_location).at(t)
    distance_km = difference.distance().km

    if distance_km < THRESHOLD_DISTANCE_KM:
        pass_lats.append(subpoint.latitude.degrees)
        pass_lons.append(subpoint.longitude.degrees)

    t += timedelta(seconds=30)

# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Use Basemap to create a world map projection
m = Basemap(projection='mill', resolution='l', ax=ax)
m.drawcoastlines()
m.drawcountries()
m.drawparallels(np.arange(-90, 90, 30), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180, 180, 60), labels=[0, 0, 0, 1])

x, y = m(lons, lats)

def split_increasing_sublists(x, y):
    """
    Splits a list into sublists where a new sublist begins when the numbers stop increasing.

    Args:

    lst: The input list.

    Returns:
    A list of sublists.
    """

    result = []
    current_sublist = []

    for current_x, current_y in list(zip(x, y)):
        if not current_sublist or current_x >= current_sublist[-1][0]:
            current_sublist.append((current_x, current_y))
        else:
            result.append(current_sublist)
            current_sublist = [(current_x, current_y)]

    if current_sublist:
        result.append(current_sublist)

    return result

# line = m.plot(x, y, 'b-', label='Satellite Ground Track', linewidth=1)
# line = m.plot([1], [1], 'b-', label='Satellite Ground Track', linewidth=1)

sublists = split_increasing_sublists(x, y)
position_frames = []
# print(sublists)
for l in sublists:
    l_x, l_y = zip(*l)
    # line = m.plot(l_x, l_y, 'b-', label='Satellite Ground Track', linewidth=1)
    line = m.plot([0], [0], 'b-', label='Satellite Ground Track', linewidth=1)
    for xy_tuple in l:
        position_frames.append((line, xy_tuple))

# obs_x, obs_y = m(ground_station_longitude, ground_station_latitude)
# m.plot(obs_x, obs_y, 'ro', markersize=8, label='Observer Location')

# for i in range(len(pass_lats)):
#     print('g')
#     pass_x, pass_y = m(pass_lons[i], pass_lats[i])
#     m.plot(pass_x, pass_y, 'go', markersize=5)

# # Add legend and title
# plt.legend(loc='upper left')
# plt.title(f'Satellite Ground Track and Passes')
# plt.show()

point = m.plot(0, 0, 'go', markersize=5)[0]

def update1(frame):
    lon_subset, lat_subset = lons[frame], lats[frame]
    x, y = m(lon_subset, lat_subset)
    point.set_data(x, y)
    return point,

def update2(frame):
    x, y = m(frame[1], frame[0])
    point.set_data(x, y)
    return point,

line_x = []
line_y = []
def update3(frame):
    x, y = m(frame[1], frame[0])
    line_x.append(x)
    line_y.append(y)
    line[0].set_xdata(line_x)
    line[0].set_ydata(line_y)
    # return line,

previous_line = None
current_line = None
line_x = []
line_y = []
def update4(frame):
    global previous_line
    global current_line
    global line_x
    global line_y

    current_line = frame[0]

    if not previous_line or current_line != previous_line:
        print('reset!!!!!!')
        line_x = []
        line_y = []

    xy_tuple = frame[1]
    x, y = xy_tuple

    # x, y = m(xy_tuple[1], xy_tuple[0])
    print(f'{current_line}, x: {x}, y:{y}')

    line_x.append(x)
    line_y.append(y)

    current_line[0].set_xdata(line_x)
    current_line[0].set_ydata(line_y)

    previous_line = current_line

    return current_line,

positions = list(zip(lats, lons))

# ani = animation.FuncAnimation(fig=fig, func=update1, frames=400, interval=30, repeat=False)
# ani = animation.FuncAnimation(fig=fig, func=update2, frames=positions, interval=30, repeat=False)
# ani = animation.FuncAnimation(fig=fig, func=update3, frames=positions, interval=30, repeat=False)
ani = animation.FuncAnimation(fig=fig, func=update4, frames=position_frames, interval=30, repeat=False)
plt.show()
