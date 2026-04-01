import argparse

from sotodlib.core import Context, FlagManager
from sotodlib import mapmaking
from sotodlib.tod_ops import flags as tod_flags

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--context", required=True)
    ap.add_argument("--query", default="1")
    ap.add_argument("--merge-into-glitch", action="store_true")
    args = ap.parse_args()

    ctx = Context(args.context)
    ids = mapmaking.get_ids(args.query, context=ctx)
    if len(ids) == 0:
        print(f"No observations found for query: {args.query}")
        return

    obs_id = ids[0]
    print(f"Using first obs id: {obs_id}")
    obs = ctx.get_obs(obs_id)

    if "flags" not in obs._fields:
        obs.wrap("flags", FlagManager.for_tod(obs))

    # print("flags keys:", list(obs.flags.keys()))

    print("Computing turnaround flags with scanspeed...")
    # This creates a new flag called "turnarounds" in obs.flags
    ta, left, right = tod_flags.get_turnaround_flags(
                    obs, method="scanspeed", name="turnarounds", truncate=True,
                    t_buffer=2, kernel_size=400, peak_threshold=0.1,
                    rel_distance_peaks=0.3,
                )

    print(f"ndet={obs.dets.count}, nsamp={obs.samps.count}")
    print("flags keys:", list(obs.flags.keys()))

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

