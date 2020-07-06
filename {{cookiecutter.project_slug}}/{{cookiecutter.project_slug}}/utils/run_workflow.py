import platform
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
    # Using individual conda environments dor each snakemake
    # rule is currently not working on Windows. Hence, the
    # following lines turn this feature off.
    use_conda = False if platform.system() == 'Windows' else True

    return snakemake(
        snakefile = Path( root_dir, SNAKE_FILE_NAME ).resolve( strict = True ),
        configfiles = [ config_file ],
        #workdir = root_dir,
        cores = num_cores,
        use_conda = use_conda,
        forceall = forceall,
        conda_create_envs_only = conda_create_envs_only,
        dryrun = dryrun,
        targets = [ target ]
    )