from pathlib import Path
from snakemake import snakemake

from .._config import SNAKE_FILE_NAME


def run_workflow(
    config_file,
    target,
    root_dir,
    forceall, 
    dryrun,
    conda_create_envs_only,
    num_cores
) :
        
    return snakemake(
        snakefile = Path( root_dir, SNAKE_FILE_NAME ).resolve( strict = True ),
        configfiles = [ config_file ],
        #workdir = root_dir,
        cores = num_cores,
        use_conda = True,
        forceall = forceall,
        conda_create_envs_only = conda_create_envs_only,
        dryrun = dryrun,
        targets = [ target ]
    )