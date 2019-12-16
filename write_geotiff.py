"""Functions to export LOFAR near-field images (in pqr) to geotiff"""

import numpy as np
from rasterio.transform import Affine
import rasterio


def normalized_earth_radius(latitude_rad):
    """
    Normalized earth radius in m, copied from lofargeo by Michiel Brentjens

    Args:
       latitude_rad: latitude in radians

    Returns:
       float: normalized earth radius in meters
    """
    wgs84_f = 1. / 298.257223563
    return 1.0 / np.sqrt(np.cos(latitude_rad)**2 +
            ((1.0 - wgs84_f)**2) * (np.sin(latitude_rad)**2))


def geographic_from_xyz(xyz_m):
    """
    Compute lon, lat, and height, copied from lofargeo by Michiel Brentjens

    Args:
        xyz_m: x, y and z coordinates

    Returns:
        lat, long, height: Latitude in degrees, longitude in degrees, height in
                           meters w.r.t. WGS84 ellipsoid
    """
    wgs84_a = 6378137.0
    wgs84_f = 1. / 298.257223563
    wgs84_e2 = wgs84_f * (2.0 - wgs84_f)

    x_m, y_m, z_m = xyz_m
    lon_rad = np.arctan2(y_m, x_m)
    r_m = np.sqrt(x_m**2 + y_m**2)

    # Iterate to latitude solution
    phi_previous = 1e4
    phi = np.arctan2(z_m, r_m)
    while abs(phi - phi_previous) > 1.6e-12:
        phi_previous = phi
        phi = np.arctan2(z_m + wgs84_e2 * wgs84_a *
                            normalized_earth_radius(phi) * np.sin(phi), r_m)

    lat_rad = phi
    height_m = r_m * np.cos(lat_rad) + z_m * np.sin(lat_rad) - \
                 wgs84_a * np.sqrt(1.0 - wgs84_e2 * np.sin(lat_rad)**2)
    return np.rad2deg(lon_rad), np.rad2deg(lat_rad), height_m


def pqr_to_longlatheight(pqr):
    """
    Convert pqr coordinates to lat, long, height

    Args:
        pqr (np.array): p, q, r coordinates in meter (r can be omitted)

    Returns:
        long, lat, height: latitude (deg), longitude (deg), height (m) (tuple)
    """
    # lofarcenter = db.phase_centres["CS002LBA"]
    lofarcenter_etrs = np.array([3826577.462, 461022.624, 5064892.526])
    # pqr_to_etrs = db.pqr_to_etrs["CS002LBA"]
    pqr_to_etrs = np.array([[-0.11959511, -0.79195445, 0.598753],
                            [0.99282275, -0.09541868, 0.072099],
                            [0.0000331, 0.60307829, 0.797682]])

    if len(pqr) == 2:
        pqr = np.array([pqr[0], pqr[1], 0.])

    etrs = pqr_to_etrs @ pqr + lofarcenter_etrs
    return geographic_from_xyz(etrs)


def save_as_geotiff(image, filename, llc, urc):
    """
    Save numpy array as GeoTiff

    Args:
        image (np.array): numpy array with image (should be 2-dimensional)
        filename (str): filename where the geotiff should be stored
        llc (Tuple(float)): lower left corner in degrees (long, lat)
        urc (Tuple(float)): upper right corner in degrees (long, lat)
    """
    image = np.squeeze(image)

    height, width = image.shape
    long_res = (urc[0] - llc[0]) / width
    lat_res = (urc[1] - llc[1]) / height

    transform = Affine.translation(llc[0] - long_res / 2,
                                   llc[1] - lat_res / 2) * \
                  Affine.scale(long_res, lat_res)

    with rasterio.open(filename, "w", driver="GTiff",
                       height=height, width=width,
                       count=1,
                       dtype=image.dtype,
                       crs='+proj=latlong',
                       transform=transform) as gtif:
        gtif.write(image, 1)
