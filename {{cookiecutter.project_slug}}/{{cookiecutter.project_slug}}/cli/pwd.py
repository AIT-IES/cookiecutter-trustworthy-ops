from argparse import ArgumentParser
from sys import exit

from ..utils.credentials_cache import CredentialsCache
from ..utils.freeze_workflow import FreezeWorkflow
from ..utils.workflow_config import WorkflowConfig


def main():

    # Command line parser.
    parser = ArgumentParser(
        description = 'Store credentials for workflow.'
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
        '-n', '--new-cache',
        action = 'store_true',
        help = 'create a new credentials cache'
    )

    parser.add_argument(
        '--no-freeze',
        action = 'store_true',
        help = 'do not check if workflow has been frozen'
    )

    # Retrieve command line arguments.
    args = parser.parse_args()

    try:
        # Check if workflow definition has remained unchanged.
        if not args.no_freeze:
            freeze = FreezeWorkflow(
                args.root_dir,
                args.verbose
            )

            if not freeze.check():
                print( '\nFreeze the workflow before storing new credentials!' )
                exit( 1 )

        # Load config file.
        workflow_config = WorkflowConfig(
            root_dir = args.root_dir
        )

        # Create new cache for credentials.
        credentials_cache = CredentialsCache(
            new_cache = args.new_cache
        )

        # Save username and password for every entry provided in the config list 'credentials'.
        for entry in workflow_config.credentials():
            credentials_cache.store( entry )

    except Exception as err:

        print( err )
        exit( 100 )


if __name__ == '__main__':
    main()
