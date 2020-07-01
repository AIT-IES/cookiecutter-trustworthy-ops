from argparse import ArgumentParser

from ..utils.freeze_workflow import FreezeWorkflow


def main():

    # Command line parser.
    parser = ArgumentParser(
        description = 'Freeze workflow.'
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

    args = parser.parse_args()

    # Create digest of all files relevant for the workflow.
    freeze = FreezeWorkflow(
        dir = args.root_dir,
        verbose = args.verbose
    )

    freeze.freeze()


if __name__ == '__main__':

    main()
