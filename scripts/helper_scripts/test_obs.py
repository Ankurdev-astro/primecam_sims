"""
Explore and demonstrate obs and meta fields from sotodlib Context.
Explore all available fields.
"""
import numpy as np
import argparse
from sotodlib.core import Context
from sotodlib import mapmaking


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def explore_axis_manager(obj, indent=0):
    """Recursively explore an AxisManager-like object, printing all fields found."""
    prefix = "  " * indent
    
    # If not an AxisManager, just print its type and basic info
    if not hasattr(obj, "_fields"):
        obj_type = type(obj).__name__
        if isinstance(obj, np.ndarray):
            print(f"{prefix}{obj_type} shape={obj.shape}, dtype={obj.dtype}")
        elif hasattr(obj, "__len__") and not isinstance(obj, str):
            print(f"{prefix}{obj_type} len={len(obj)}")
        else:
            val_str = str(obj)[:80]
            print(f"{prefix}{obj_type}: {val_str}")
        return
    
    # Iterate through all fields in AxisManager
    for field in obj._fields:
        try:
            val = obj[field]
            if hasattr(val, "_fields"):
                # Nested AxisManager
                print(f"{prefix}{field}:")
                explore_axis_manager(val, indent + 1)
            elif isinstance(val, np.ndarray):
                print(f"{prefix}{field}: ndarray shape={val.shape}, dtype={val.dtype}")
            elif hasattr(val, "__len__") and not isinstance(val, str):
                print(f"{prefix}{field}: {type(val).__name__} len={len(val)}")
            else:
                val_str = str(val)[:60]
                print(f"{prefix}{field}: {type(val).__name__} = {val_str}")
        except Exception as e:
            print(f"{prefix}{field}: ERROR - {e}")


def main():
    ap = argparse.ArgumentParser(
        description="Explore obs and meta structures from sotodlib"
    )
    ap.add_argument("-c", "--context", required=True, 
                    help="Path to context YAML file")
    ap.add_argument("--query", default="1",
                    help="Query string to select observations")
    args = ap.parse_args()

    # Load context
    ctx = Context(args.context)
    print(f"Context loaded from: {args.context}")
    
    # Get observation IDs
    ids = mapmaking.get_ids(args.query, context=ctx)
    if len(ids) == 0:
        print("No observations found matching query.")
        return

    print(f"Found {len(ids)} observation(s). Using first one.")
    obs_id = ids[0]
    print(f"Obs ID: {obs_id}")

    # ===== GET_OBS =====
    print_section("GET_OBS - Observation Data Structure")
    obs = ctx.get_obs(obs_id)
    explore_axis_manager(obs, indent=0)

    # ===== GET_META =====
    print_section("GET_META - Observation Metadata Structure")
    try:
        meta = ctx.get_meta(obs_id)
        explore_axis_manager(meta, indent=0)
    except Exception as e:
        print(f"ERROR loading meta: {e}")

    print_section("DONE")


if __name__ == "__main__":
    main()
