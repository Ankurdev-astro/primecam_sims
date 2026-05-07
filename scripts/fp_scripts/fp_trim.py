import numpy as np
import os

import toast
from toast.utils import Logger
from astropy.table import QTable


def build_fp_file(requested_dets, fp_dir="./input_files/fp_files/"):
    """Build or reuse the trimmed w2 focalplane file and return (ndets_selected, path)."""
    # Load the full detector table once; the w2 subset is the only one used here.
    hf_fulltable_file = os.path.join(fp_dir, "fp_f280_dettable.h5")
    dettable_full = QTable.read(hf_fulltable_file, path='dettable_stack')

    # Keep only w2 detectors before applying the requested-count clamp.
    trim_dettable_w2 = dettable_full[dettable_full['wafer_slot'] == 'w2']
    if requested_dets < 10 or requested_dets % 2 != 0:
        raise ValueError("requested_dets must be an even number and at least 10.")

    # Never request more detectors than exist in w2.
    ndets_selected = min(requested_dets, len(trim_dettable_w2))
    if ndets_selected != requested_dets:
        # Route the clamp message through TOAST logging instead of stdout.
        Logger.get().info(
            f"Requested dets ({requested_dets}) exceeds the total number of "
            f"detectors in w2 ({len(trim_dettable_w2)} dets); using {ndets_selected} instead."
        )

    # This is the exact file name the simulation will reuse later.
    focalplane_file = f"dets_FP_PC280_{ndets_selected}_w2.h5"
    fp_filename = os.path.join(fp_dir, focalplane_file)

    if not os.path.exists(fp_filename):
        # Select evenly spaced detector pairs and write the trimmed focalplane file.
        first_index = trim_dettable_w2["index"][0]
        last_index = trim_dettable_w2["index"][-1]
        pairs_select = ndets_selected // 2
        linspace_indices = np.linspace(first_index, last_index, pairs_select, dtype=int)
        pixels_select = trim_dettable_w2[np.isin(trim_dettable_w2["index"], linspace_indices)]['pixel']
        pixel_strings = [f"{int(pixel):04}".encode('utf-8') for pixel in pixels_select]
        mask = np.isin(trim_dettable_w2['pixel'], pixel_strings)
        trim_dettable_w2[mask].write(
            fp_filename,
            path='dettable_trim',
            serialize_meta=True,
            overwrite=True,
        )

    return ndets_selected, fp_filename
