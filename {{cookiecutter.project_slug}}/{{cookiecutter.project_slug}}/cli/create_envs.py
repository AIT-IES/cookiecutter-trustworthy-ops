from argparse import ArgumentParser
from datetime import datetime
from sys import exit

from ..utils.credentials_cache import CredentialsCache
from ..utils.freeze_workflow import FreezeWorkflow
from ..utils.workflow_config import WorkflowConfig
from ..utils.run_workflow import run_workflow


def main():

    # Command line parser.
    parser = ArgumentParser(
        description = 'Create conda environments for all workflow steps.'
    )

    parser.add_argument(
        'root_dir',
        nargs = '?',
        default = '.',
        metavar = '{{ cookiecutter.project_slug | upper }}_DIR',
        help = 'workflow root directory'
    )

    # Retrieve command line arguments.
    args = parser.parse_args()

    try:
        # Initialise credentials cache (for further use during the snakemake workflow).
        credentials_cache = CredentialsCache(
            new_cache = False
        )
    
        # Load config file.
        workflow_config = WorkflowConfig( 
            root_dir = args.root_dir 
        )

        # Execute the snakemake workflow once.
        if not run_workflow( 
            config_file = workflow_config.file_path(),
            target = workflow_config.target().format( run_id = 'TMP' ),
            root_dir = args.root_dir,
            forceall = True,
            dryrun = False,
            conda_create_envs_only = True,
            num_cores = workflow_config.num_cores()
        ):
            exit( 2 )

    except Exception as err:

        print( err )
        exit( 100 )


if __name__ == '__main__':
    main()
