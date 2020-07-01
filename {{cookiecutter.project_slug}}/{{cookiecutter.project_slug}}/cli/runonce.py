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
        description = 'Run workflow once.'
    )

    parser.add_argument(
        'root_dir',
        nargs = '?',
        default = '.',
        metavar = '{{ cookiecutter.project_slug | upper }}_DIR',
        help = 'workflow root directory'
    )

    parser.add_argument(
        '-v', '--verbose',
        action = 'store_true',
        help = 'output additional information'
    )

    parser.add_argument(
        '-f', '--forceall',
        action = 'store_true',
        help = 'force all output files to be re-created'
    )

    parser.add_argument(
        '-d', '--dryrun',
        action = 'store_true',
        help = 'only dry-run the workflow'
    )

    parser.add_argument(
        '--no-freeze',
        action = 'store_true',
        help = 'do not check if workflow has been frozen'
    )

    parser.add_argument(
        '--no-cache',
        action = 'store_true',
        help = 'do not load credentials cache'
    )

    # Retrieve command line arguments.
    args = parser.parse_args()

    try:
        # Check if workflow definition has remained unchanged.
        if not args.no_freeze:
            freeze = FreezeWorkflow(
                dir = args.root_dir,
                verbose = args.verbose
            )

            if not freeze.check():
                print( '\nFreeze the workflow before executing it!' )
                exit( 1 )

        # Initialise credentials cache (for further use during the snakemake workflow).
        if not args.no_cache:
            credentials_cache = CredentialsCache(
                new_cache = False
            )

        # Load config file.
        workflow_config = WorkflowConfig(
            root_dir = args.root_dir
        )

        # Define run ID.
        run_id = workflow_config.run_id_format().format( datetime.now() )

        # Execute the snakemake workflow once.
        if not run_workflow(
            config_file = workflow_config.file_path(),
            target = workflow_config.target().format( run_id = run_id),
            root_dir = args.root_dir,
            forceall = args.forceall,
            dryrun = args.dryrun,
            conda_create_envs_only = False,
            num_cores = workflow_config.num_cores()
        ):
            exit( 2 )

    except Exception as err:

        print( err )
        exit( 100 )


if __name__ == '__main__':
    main()
