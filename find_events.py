from skyfield.api import wgs84, load, EarthSatellite
from datetime import datetime, timedelta


ts = load.timescale()

satellite = EarthSatellite(
    '1 00001U          23274.66666667  .00000000  00000-0  00000-0 0 00001',
    '2 00001 097.3597 167.6789 0009456 299.5645 340.3650 15.25701051000010',
    'SOSO-1',
    ts
)

bluffton = wgs84.latlon(+40.8939, -83.8917)

# t0 = ts.utc(2014, 1, 23)
# t1 = ts.utc(2014, 1, 24)
t0 = ts.now()
t1 = t0 + timedelta(days=5)

t, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=30.0)

event_names = 'rise above 30°', 'culminate', 'set below 30°'

for ti, event in zip(t, events):
    name = event_names[event]
    print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)
