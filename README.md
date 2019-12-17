# LOFAR GeoTIFF

This package provides a simple function to write LOFAR near field images as
a GeoTIFF file. This makes sure that some metadata is kept, in particular the
location of the image.

## Installation

`pip install lofargeotiff`

## Usage

Using as input a two-dimensional numpy array of pixel values, and the PQ
coordinates of the (center of the) lower left and upper right pixel, the
following command writes a GeoTIFF:

```python
from lofargeotiff import write_geotiff
import numpy as np

data = np.random.rand(400, 400)
lowerleft = (-200, -200)
upperright = (200, 200)

write_geotiff(data, "test.tif", lowerleft, upperright,
              obsdate="2016-02-12 08:00:00",
              tags={"Author": "Tammo Jan Dijkema",
                    "Project": "EOR"})
```

The resulting file can be read back into python using `rasterio.open`, or any
other package that reads TIFF. The metadata can be inspected on the command
line with `exiftool`.
