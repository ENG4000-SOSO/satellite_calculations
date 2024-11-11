from skyfield.api import Topos, load, EarthSatellite
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
from typing import List, Optional, Any
import json
import os
from pathlib import Path


def clear_xdata(plot):
    plot.set_xdata([])


def clear_ydata(plot):
    plot.set_ydata([])


def get_xdata(plot):
    return plot.get_xdata()


def get_ydata(plot):
    return plot.get_ydata()


def set_xdata(plot, xdata):
    plot.set_xdata(xdata)


def set_ydata(plot, ydata):
    plot.set_ydata(ydata)


def concat_xdata(plot, x):
    xdata = get_xdata(plot)

    new_xdata = np.concatenate((xdata, [x]))

    set_xdata(plot, new_xdata)


def concat_ydata(plot, y):
    ydata = get_ydata(plot)

    new_ydata = np.concatenate((ydata, [y]))

    set_ydata(plot, new_ydata)


THRESHOLD_DISTANCE_KM = 1000


class Point:
    def __init__(self, x, y, latitude, longitude, time, distances, line: Optional[Any] = None):
        self.latitude = latitude
        self.longitude = longitude
        self.x = x
        self.y = y
        self.distances = distances
        self.close_pass = any(distance < THRESHOLD_DISTANCE_KM for distance in distances.values())
        self.line = line
        self.time = time
        self.text = None

    def initialize_line(self, line):
        clear_xdata(line[0])
        clear_ydata(line[0])
        self.line = line[0]


def split_increasing_sublists(points: List[Point]) -> List[List[Point]]:
    """
    Splits a list into sublists where a new sublist begins when the numbers stop
    increasing.
    """

    result: List[List[Point]] = []
    current_sublist: List[Point] = []

    for point in points:
        if not current_sublist or point.x <= current_sublist[-1].x:
            current_sublist.append(point)
        else:
            result.append(current_sublist)
            current_sublist = [point]

    if current_sublist:
        result.append(current_sublist)

    return result


class GroundStation:
    def __init__(self, name, x, y, latitude, longitude, topos, point: Optional[Any] = None):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.x = x
        self.y = y
        self.topos = topos
        self.point = point

    def initialize_point(self, point):
        clear_xdata(point)
        clear_ydata(point)
        self.point = point


# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Use Basemap to create a world map projection
m = Basemap(projection='mill', resolution='l', ax=ax)
m.drawcoastlines()
m.drawcountries()
m.drawparallels(np.arange(-90, 90, 30), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180, 180, 60), labels=[0, 0, 0, 1])

ground_stations: List[GroundStation] = []

with open('ground_stations.json') as f:
    ground_stations_dict = json.load(f)
    for ground_station in ground_stations_dict:
        lat = ground_station['latitude']
        lon = ground_station['longitude']
        height = ground_station['height']
        topos = Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=height)
        x, y = m(lon, lat)
        ground_station = GroundStation(ground_station['name'], x, y, lat, lon, topos)
        ground_stations.append(ground_station)

ts = load.timescale()

satellite = EarthSatellite(
    '1 00001U          23274.66666667  .00000000  00000-0  00000-0 0 00001',
    '2 00001 097.3597 167.6789 0009456 299.5645 340.3650 15.25701051000010',
    'SOSO-1',
    ts
)

t_start = ts.now()
t_end = ts.now() + timedelta(days=1)

points = []

t = t_start
while t < t_end:

    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()

    lat = subpoint.latitude.degrees
    lon = subpoint.longitude.degrees
    x, y = m(lon, lat)

    distances = {}
    for ground_station in ground_stations:
        difference = (satellite - ground_station.topos).at(t)
        distances[ground_station.name] = difference.distance().km

    p = Point(x, y, lat, lon, t, distances)
    points.append(p)

    t += timedelta(seconds=30)

sublists: List[List[Point]] = split_increasing_sublists(points)

for sublist in sublists:
    line = m.plot([0], [0], 'b-', label='Satellite Ground Track', linewidth=1)
    for point in sublist:
        point.initialize_line(line)

for ground_station in ground_stations:
    m.plot(ground_station.x, ground_station.y, 'ro', markersize=8, label='Observer Location')
    ax.annotate(ground_station.name, (ground_station.x, ground_station.y), fontsize=16, color='red')

# Satellite
point = m.plot(0, 0, 'go', markersize=5)[0]
text = ax.annotate(satellite.name, xy=(0, 0), fontsize=14, color='Green')
text2 = ax.annotate('', xy=(0, 0), fontsize=25)


def update5(frame: Point):
    x = frame.x
    y = frame.y

    print(f'{frame.line}, x: {x}, y:{y}')

    concat_xdata(frame.line, x)
    concat_ydata(frame.line, y)

    if frame.close_pass:
        m.plot(x, y, 'go', markersize=8)

    set_xdata(point, x)
    set_ydata(point, y)
    text.set_position((x,y))
    text2.set_text(frame.time.utc_strftime('%b %d, %Y at %H:%M:%S UTC'))


ani = animation.FuncAnimation(fig=fig, func=update5, frames=points, interval=3, repeat=False)

plt.show()
