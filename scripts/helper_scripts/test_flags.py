import argparse
import numpy as np

from sotodlib.core import Context, FlagManager
from sotodlib import mapmaking
from sotodlib.tod_ops import flags as tod_flags


def print_debug_stats(obs, prefix=""):
    az = np.asarray(obs.boresight.az)
    ts = np.asarray(obs.timestamps)
    print(
        f"{prefix}Input stats:",
        f"az shape={az.shape}",
        f"ts shape={ts.shape}",
        f"finite az={np.isfinite(az).sum()}/{az.size}",
        f"finite ts={np.isfinite(ts).sum()}/{ts.size}",
        sep=" | ",
    )
    if az.size > 0:
        finite_az = az[np.isfinite(az)]
        if finite_az.size > 0:
            print(
                f"{prefix}az finite stats:",
                f"dtype={finite_az.dtype}",
                f"min={finite_az.min():.6g}",
                f"max={finite_az.max():.6g}",
                f"ptp={np.ptp(finite_az):.6g}",
                sep=" | ",
            )
            print(
                f"{prefix}az samples:",
                f"first3={finite_az[:3]}",
                f"last3={finite_az[-3:]}",
                sep=" | ",
            )
            az_step = np.diff(finite_az)
            if az_step.size > 0:
                p95 = np.percentile(az_step, 95)
                gt95 = az_step[az_step > p95]
                ge95 = az_step[az_step >= p95]
                print(
                    f"{prefix}daz stats (sotodlib-like):",
                    f"size={az_step.size}",
                    f"min={az_step.min():.6g}",
                    f"max={az_step.max():.6g}",
                    f"median={np.median(az_step):.6g}",
                    f"p95={p95:.6g}",
                    sep=" | ",
                )
                print(
                    f"{prefix}daz percentile masks:",
                    f"count(>p95)={gt95.size}",
                    f"count(>=p95)={ge95.size}",
                    sep=" | ",
                )
                if gt95.size > 0:
                    print(f"{prefix}approx_daz using >p95 median: {np.median(gt95):.6g}")
                else:
                    print(f"{prefix}approx_daz using >p95 median: EMPTY -> NaN in sotodlib")
                if ge95.size > 0:
                    print(f"{prefix}approx_daz using >=p95 median: {np.median(ge95):.6g}")
            else:
                print(f"{prefix}daz stats (sotodlib-like): no differences available")
        else:
            print(f"{prefix}az finite stats: no finite az values")

    if az.size > 1 and ts.size > 1:
        valid = np.isfinite(az) & np.isfinite(ts)
        if valid.sum() > 1:
            dts = np.diff(ts[valid])
            daz = np.diff(az[valid])
            good = dts != 0
            if good.sum() > 0:
                scanspeed = np.abs(daz[good] / dts[good])
                finite_scanspeed = scanspeed[np.isfinite(scanspeed)]
                print(
                    f"{prefix}Derived scanspeed stats:",
                    f"samples={finite_scanspeed.size}",
                    f"median={np.median(finite_scanspeed):.6g}" if finite_scanspeed.size else "median=nan",
                    f"min={finite_scanspeed.min():.6g}" if finite_scanspeed.size else "min=nan",
                    f"max={finite_scanspeed.max():.6g}" if finite_scanspeed.size else "max=nan",
                    sep=" | ",
                )
            else:
                print(f"{prefix}Derived scanspeed stats: all adjacent timestamps are identical (dt=0)")
        else:
            print(f"{prefix}Derived scanspeed stats: fewer than 2 valid (finite az & ts) samples")


def process_obs(ctx, obs_id, idx=None, total=None, method="scanspeed", debug=False):
    prefix = f"[{idx + 1}/{total}] " if idx is not None and total is not None else ""
    obs = ctx.get_obs(obs_id)

    if "flags" not in obs._fields:
        obs.wrap("flags", FlagManager.for_tod(obs))

    if debug:
        print(f"{prefix}Processing obs id: {obs_id}")
        print(f"{prefix}Computing turnaround flags with method={method}...")
        print_debug_stats(obs, prefix=prefix)

    # This creates a new flag called "turnarounds" in obs.flags
    if method == "scanspeed":
        ta, left, right = tod_flags.get_turnaround_flags(
            obs,
            method="scanspeed",
            name="turnarounds",
            truncate=True,
            t_buffer=2,
            kernel_size=400,
            peak_threshold=0.1,
            rel_distance_peaks=0.3,
        )
    else:
        ta = tod_flags.get_turnaround_flags(
            obs,
            method="az",
            name="turnarounds",
            truncate=True,
            t_buffer=2,
            merge_subscans=False,
        )

    print(f"{prefix}ndet={obs.dets.count}")
    print(f"{prefix}flags keys: {list(obs.flags.keys())}")
    print(f"{prefix}{method}-method segments (det0): {ta[0].ranges().shape[0]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-c",
        "--context",
        default="ccat_datacenter_mock/context/context.yaml",
        help="Path to the sotodlib context YAML",
    )
    ap.add_argument("--query", default="1")
    ap.add_argument("--merge-into-glitch", action="store_true")
    ap.add_argument("--debug", action="store_true", default=False)
    ap.add_argument("--method", choices=["scanspeed", "az"], default="scanspeed")
    args = ap.parse_args()

    ctx = Context(args.context)
    ids = mapmaking.get_ids(args.query, context=ctx)
    if len(ids) == 0:
        print(f"No observations found for query: {args.query}")
        return

    print(f"Found {len(ids)} observations for query: {args.query}")
    ok = 0
    failed = 0
    for i, obs_id in enumerate(ids):
        try:
            process_obs(
                ctx,
                obs_id,
                idx=i,
                total=len(ids),
                method=args.method,
                debug=args.debug,
            )
            ok += 1
        except Exception as exc:
            failed += 1
            print(f"[{i + 1}/{len(ids)}] ERROR for obs id {obs_id}: {type(exc).__name__}: {exc}")
            print("Continuing to next observation...")

    print(f"Finished processing observations: success={ok}, failed={failed}, total={len(ids)}")

    ### --------------------------------------------- ###
    ### DEBUG:
    ### Do not merge turnaround flags into glitch_flags
    ### This is just a check
    ##print("scan-method segments (det0):", ta[0].ranges().shape[0])

    ### Update the flag used by MLMapmaker cuts
    ### If glitch_flags already exists, merge turnaround flags into it using bitwise OR
    ##if "glitch_flags" in obs.flags:
    ##    obs.flags["glitch_flags"] |= ta
    ### Otherwise, create new glitch_flags entry with turnaround flags
    ##else:
    ##    obs.flags.wrap("glitch_flags", ta, [(0, "dets"), (1, "samps")])

    ### Get the glitch_flags RangesMatrix
    ##gf = obs.flags["glitch_flags"]
    ### Extract the ranges for detector 0
    ##r0 = gf[0].ranges()
    ### Print total number of flagged segments for detector 0
    ##print("glitch_flags (det0) segments:", r0.shape[0])
    ### Print the first 5 range segments for detector 0
    ### print("glitch_flags (det0) first ranges:", r0[:])
    ### --------------------------------------------- ###

if __name__ == "__main__":
    main()

