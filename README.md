# primecam_sims
PrimeCam Simulations for timestream data and Mapmaking
Note: High memory usage expected. Run only on a cluster

Auxiliary files needed: 
[pysm3_map_nside2048_allStokes.fits](https://www.dropbox.com/scl/fi/gm4xuhguht5dx848d9e69/pysm3_map_nside2048_allStokes.fits?rlkey=0qga1dkj6442vxrnvku3pcrlx&dl=0)

This file should be put inside `./input_files/`

### First let's start with timestream simulation.

Usage: `python sim_data_primecam.py --test-run`
For full production run: `python sim_data_primecam.py`

This shall create 'ccat_datacenter_mock' dir. All observations are stored here. 
Context dir and Maximum-Likelihood Map outputs will be stored here.

### Next: Processing and Map-making pipeline:

Usage: 
`primecam_integrated_pipeline.py --h5-dirs ./ccat_datacenter_mock/path_to_obs_dir`

`--h5-dir` can take multiple args: to load all obs, for example:
`primecam_integrated_pipeline.py --h5-dirs ./ccat_datacenter_mock/sim_PCAM280_h5_Deep56*`


#### Config file for ML Mapmaker:
```
dump-write: False #Set to True if writing maps at intermediate steps is needed
maxiter: set to a lower value for quick testing
```
