"""Taken and modified from the zipcode 2.0.0 -- was having issues with sqlite threading and since I had zipcode data
already, I just swiped the function I needed and modified for use with my zipcode model."""
from haversine import haversine
import math

from .models import ZipCode


def zips_in_radius(zip, distance):
    """Given a a zip code string and a distance in miles, returns a list of zipcodes within the distance radius."""
    zips = []

    if not isinstance(zip, str):
        raise TypeError('zip must be a string.')

    if not isinstance(distance, int):
        raise TypeError('distance must be an int.')

    zipcode = ZipCode.objects.get(zip=zip)

    dist_btwn_lat_deg = 69.172
    dist_btwn_lon_deg = math.cos(zipcode.lat) * dist_btwn_lat_deg
    lat_degr_rad = float(distance) / dist_btwn_lat_deg
    lon_degr_rad = float(distance) / dist_btwn_lon_deg

    latmin = zipcode.lat - lat_degr_rad
    latmax = zipcode.lat + lat_degr_rad
    lonmin = zipcode.long - lon_degr_rad
    lonmax = zipcode.long + lon_degr_rad

    if latmin > latmax:
        latmin, latmax = latmax, latmin
    if lonmin > lonmax:
        lonmin, lonmax = lonmax, lonmin

    results = ZipCode.objects.filter(
        long__gt=lonmin,
        long__lt=lonmax,
        lat__gt=latmin,
        lat__lt=latmax,
    )

    for z in results:
        if haversine((zipcode.lat, zipcode.long), (z.lat, z.long)) <= distance:
            zips.append(z)

    return zips
