"""
Originally from sotodlib
Script to write geometry files
Needs Context DB in ./context/ dir

Edit: Map centre
"""


import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--context', 
        default='ccat_datacenter_mock/context/context.yaml')
args = parser.parse_args()

from sotodlib import core, coords
import numpy as np
from pixell import enmap
from so3g import proj

DEG = np.pi/180

print('Init context...')
ct = core.Context(args.context)

print('Load obs list...')
obs = ct.obsdb.query()

# Map -- center at (RA, DEC) , choosing 0.25 arcmin per pixel
wcsk = coords.get_wcs_kernel('car', 16, -2.0, 0.5/60.*DEG)

geoms = []
for o in obs:
    print(o)
    tod = ct.get_obs(o)
    # Promote TOD?
    fm = core.FlagManager.for_tod(tod)
    P = coords.P.for_tod(tod)
    geom = coords.get_footprint(tod, wcsk)

    geoms.append(geom)

geom = coords.get_supergeom(*geoms)
print(geom)
enmap.write_map_geometry('./ccat_datacenter_mock/context/geom.fits', *geom)
print(f"Wrote map geometry to './ccat_datacenter_mock/context/geom.fits'")
