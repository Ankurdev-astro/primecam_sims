"""
Plot ML-Mapmaker FITS maps (Intensity only).
- Uses first slice if the FITS is a cube.
- Rolls horizontally, crops along X (columns), and plots with CAR WCS.
"""

import numpy as np
from astropy.io import fits
import astropy.units as u
from astropy.wcs import WCS
import argparse
import os
from urllib.request import urlretrieve
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def _force_2d_first_slice(data):
    while data.ndim > 2:
        data = data[0]
    if data.ndim != 2:
        raise ValueError(f"Expected 2D image; got {data.shape}")
    return np.asarray(data)


def plot_deep56ML(fits_file, vmin, vmax, save, title):
    with fits.open(fits_file) as hdul:
        data = hdul[0].data

    # Force to 2D
    image2d = _force_2d_first_slice(data)

    # Roll ALONG X (columns)
    starting_idx = 20000
    rolled = np.roll(image2d, +starting_idx, axis=1)

    # Crop ALONG X (columns)
    lower_index = 15500
    upper_index = 24500
    nx = rolled.shape[1]
    li = max(0, min(nx, int(lower_index)))
    ui = max(0, min(nx, int(upper_index)))
    if ui <= li:
        raise ValueError(f"Empty x-crop after clamping: li={li}, ui={ui}, nx={nx}")

    # Convert K -> µK and crop columns; keep all rows
    cropped = (rolled[:, li:ui]) * 1e6

    # Flip left-right so RA increases to the left
    cropped = np.fliplr(cropped)

    height, width = cropped.shape

    # Build simple CAR WCS centered on Deep56
    CRPIX1 = width / 2
    CRPIX2 = height / 2
    ra_center = 16.0 * u.deg
    dec_center = -2.0 * u.deg
    resolution = 0.5 * u.arcmin.to(u.degree)

    wcs_header = fits.Header()
    wcs_header["CTYPE1"] = "RA---CAR"
    wcs_header["CUNIT1"] = "deg"
    wcs_header["CRVAL1"] = ra_center.value
    wcs_header["CDELT1"] = resolution
    wcs_header["CRPIX1"] = CRPIX1
    wcs_header["CTYPE2"] = "DEC--CAR"
    wcs_header["CUNIT2"] = "deg"
    wcs_header["CRVAL2"] = dec_center.value
    wcs_header["CDELT2"] = resolution
    wcs_header["CRPIX2"] = CRPIX2
    wcs_new = WCS(wcs_header)

    # Treat zeros as missing
    cropped[cropped == 0] = np.nan

    # Plot
    fig = plt.figure(figsize=(20, 8))
    ax = plt.subplot(projection=wcs_new)

    # Colormap (Planck parchment)
    from matplotlib.colors import ListedColormap
    cmap_url = "https://github.com/zonca/paperplots/raw/master/data/Planck_Parchment_RGB.txt"
    planck_cmap = os.path.basename(cmap_url)
    if not os.path.exists(planck_cmap):
        urlretrieve(cmap_url, planck_cmap)
    colombi1_cmap = ListedColormap(np.loadtxt(planck_cmap) / 255.0)
    colombi1_cmap.set_bad("gray")
    cmap = colombi1_cmap

    image = ax.pcolormesh(cropped, cmap=cmap, vmin=vmin, vmax=vmax)

    # RA/Dec formatting in decimal degrees
    ra = ax.coords[0]
    dec = ax.coords[1]
    ra.set_ticks_position('b')
    dec.set_ticks_position('l')
    ra.set_ticklabel_position('b')
    dec.set_ticklabel_position('l')
    ra.set_format_unit(u.deg)
    dec.set_format_unit(u.deg)
    ra.set_axislabel('Right Ascension (degrees)', fontsize=12, minpad=1)
    ra.set_axislabel_position('b')
    dec.set_axislabel('Declination (degrees)', fontsize=12, minpad=1)
    dec.set_axislabel_position('l')
    ra.display_minor_ticks(True)
    dec.display_minor_ticks(True)

    # RA increases to the left
    ax.invert_xaxis()
    ax.tick_params(axis="both", which="major", labelsize=16)

    cbar = plt.colorbar(image, ax=ax, orientation="horizontal", fraction=0.05, pad=0.15, aspect=20)
    cbar.set_label(r"Intensity [$\mu$K]", size=18, weight="bold")
    cbar.ax.tick_params(labelsize=14)

    if title:
        plt.title(title.replace(r"\n", "\n"), fontsize=22, fontweight="bold")

    if save:
        plt.savefig(save, bbox_inches="tight")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot a Deep56 FITS image of ML maps",
        epilog="The vmin and vmax unit is in [uK]",
    )
    parser.add_argument("fits_file", type=str, help="Path to the FITS file.")
    parser.add_argument("--vmin", type=float, default=-300, help="Minimum data value for colormap.")
    parser.add_argument("--vmax", type=float, default=300, help="Maximum data value for colormap.")
    parser.add_argument("--save", type=str, help="Path to save the output plot.")
    parser.add_argument(
        "--title",
        type=str,
        default="Deep 56 Field with mock 280GHz PrimeCam: \n100 dets, ~100 Hours",
        help="Title for the plot",
    )
    args = parser.parse_args()
    plot_deep56ML(args.fits_file, args.vmin, args.vmax, args.save, args.title)


if __name__ == "__main__":
    main()
