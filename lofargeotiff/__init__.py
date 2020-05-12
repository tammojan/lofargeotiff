"""Functions to export LOFAR near-field images (in pqr) to geotiff"""

import datetime
import rasterio
import lofarantpos.db
import lofarantpos.geo
import numpy as np
from rasterio.transform import Affine
import rasterio.crs


def pqr_to_longlatheight(pqr, stationname):
    """
    Convert pqr coordinates to lat, long, height

    Args:
        pqr (Tuple or np.array of length 2 or 3): p, q, r coordinates in meter
                                                  (r can be omitted)
        stationname (str): center station of the coordinate system

    Returns:
        long, lat, height: latitude (deg), longitude (deg), height (m) (tuple)
    """
    db = lofarantpos.db.LofarAntennaDatabase()
    center_etrs = db.phase_centres[stationname]
    pqr_to_etrs = db.pqr_to_etrs[stationname]

    # Append r=0 if not given
    if len(pqr) == 2:
        pqr = np.array([pqr[0], pqr[1], 0.])

    etrs = pqr_to_etrs.dot(pqr) + center_etrs
    llh_dict = lofarantpos.geo.geographic_from_xyz(etrs)
    return (np.rad2deg(llh_dict["lon_rad"]),
            np.rad2deg(llh_dict["lat_rad"]),
            llh_dict["height_m"])


def write_geotiff(image, filename, llc, urc, as_pqr=True,
                  stationname="CS002LBA", obsdate=None, tags=None):
    """
    Save numpy array as GeoTiff

    Args:
        image (np.array): numpy array with image (should be 2-dimensional)
        filename (str): filename where the geotiff should be stored
        llc (Tuple(float)): lower left corner in degrees (long, lat) or pqr (m)
                            (coordinate of center of lower left pixel)
        urc (Tuple(float)): upper right corner in degrees (long, lat) or pqr (m)
                            (coordinate of center of upper right pixel)
        as_pqr (bool): interpret llc and urc as pqr coordinates in meters
        stationname (str): center station in case of pqr coordinates
        obsdate (datetime or string): date of the observation
        tags (Dict[str]): dict with additional metadata e.g. {"Author": "Jan"}

    Example:
        >>> write_geotiff(data, "test.tif", (-200, -200), (200, 200),
                          stationname="CS002LBA",
                          obsdate="2016-02-12 08:00:00",
                          tags={"Author": "Tammo Jan Dijkema",
                                "Project": "EOR"})

        >>> write_geotiff(data, "test.tif",
                          (6.86686, 52.91332), (6.87281, 52.91692),
                          as_pqr=False)
    """
    image = np.squeeze(image)

    height, width = image.shape

    if as_pqr:
        llc = pqr_to_longlatheight(llc, stationname)
        urc = pqr_to_longlatheight(urc, stationname)

    if llc[1] < urc[1]:
        llc = list(llc)
        urc = list(urc)
        # Flip latitude; latitude of llc must be largest (only tested on lat>0)
        llc[1], urc[1] = urc[1], llc[1]
        image = image[::-1, :]


    long_res = (urc[0] - llc[0]) / width
    lat_res = (urc[1] - llc[1]) / height

    transform = Affine.translation(llc[0] - long_res / 2,
                                   llc[1] - lat_res / 2) * \
                  Affine.scale(long_res, lat_res)

    if isinstance(obsdate, datetime.datetime):
        datestr = obsdate.strftime("%Y-%m-%d %H:%M:%S")
    elif obsdate is not None:
        datestr = obsdate

    with rasterio.open(filename, "w", driver="GTiff",
                       height=height, width=width,
                       count=1, dtype=image.dtype.__str__(),
                       crs=rasterio.crs.CRS.from_epsg(4326), transform=transform) as gtif:
        gtif.write(image, 1)
        if obsdate is not None:
            gtif.update_tags(TIFFTAG_DATETIME=datestr)
            gtif.update_tags(obsdate=datestr)
        if tags is not None:
            gtif.update_tags(**tags)
