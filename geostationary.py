from skyfield.api import EarthSatellite, load
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta


# Load TLE data
tle_line1 = "1 41987U 17023A   23283.18765165  .00000000  00000-0  0  9996"
tle_line2 = "2 41987  0.0000   0.0000 0000000  0.0000  0.0000 14.98079142412921"

ts = load.timescale()
# satellite = EarthSatellite(tle_line1, tle_line2, "NAME", ts)
satellite = EarthSatellite(
    '1 42525U 18016A   23283.11958293  .00000000  00000-0  0  9996',
    '2 42525  0.0000   0.0000 0000000  0.0000  0.0000 14.98088827356309',
    "NAME",
    ts
)


# Choose a specific time
# time = ts.from_datetime(datetime(2024, 10, 28))
time = ts.utc(ts.now().utc_datetime() + timedelta(minutes=1500))

# Calculate geocentric position
geocentric = satellite.at(time)

# Convert to geographic coordinates
lat, lon = geocentric.subpoint().latitude, geocentric.subpoint().longitude

# Create a Basemap
m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='l')
m.drawcoastlines()
m.drawcountries()
m.drawmeridians(np.arange(0, 360, 30))
m.drawparallels(np.arange(-90, 90, 30))

# Plot the satellite's position
x, y = m(lon.degrees, lat.degrees)
m.plot(x, y, 'ro', markersize=10)

plt.show()
