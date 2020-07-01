from argparse import ArgumentParser
from datetime import timedelta, datetime
from time import sleep

from ..utils.credentials_cache import CredentialsCache
from ..utils.freeze_workflow import FreezeWorkflow
from ..utils.workflow_config import WorkflowConfig
from ..utils.run_workflow import run_workflow


def main():

    # Command line parser.
    parser = ArgumentParser(
        description = 'Run workflow periodically. The default period is one day.'
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
        '-N', '--num-loops',
        default = -1,
        type = int,
        help = 'specify maximum number of loops'
    )

    parser.add_argument(
        '-D', '--days',
        default = 0,
        type = int,
        help = 'loop period days'
    )

    parser.add_argument(
        '-H', '--hours',
        default = 0,
        type = int,
        help = 'loop period hours'
    )

    parser.add_argument(
        '-M', '--minutes',
        default = 0,
        type = int,
        help = 'loop period minutes'
    )

    parser.add_argument(
        '-S', '--seconds',
        default = 0,
        type = int,
        help = 'loop period seconds'
    )

    parser.add_argument(
        '-r', '--retry-delay',
        default = 60,
        type = int,
        help = 'delay in seconds for retrying to run a failed workflow execution'
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

    if ( args.days == 0 and
         args.hours == 0 and
         args.minutes == 0 and
         args.seconds == 0 ):
        # If nothing else is specified, set default period to 1 day.
        args.days = 1

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

        # Define loop period.
        period = timedelta(
            days = args.days,
            hours = args.hours,
            minutes = args.minutes,
            seconds = args. seconds
        )

        # Loop counter.
        i_loop = 1

        # Use a simple while loop and the time.sleep method for the periodic execution of
        # the workflow. More complex solutions (and especially solutions using threads) will
        # most likely break the functionality of snakemake and of the credentials cache.
        while( args.num_loops < 0 or i_loop <= args.num_loops ):

            # Save time of loop start.
            start = datetime.now()

            if not args.no_freeze and not freeze.check():
                print( '\nSomething has changed while running the workflow!' )
                exit( 1 )

            # Define run ID.
            run_id = workflow_config.run_id_format().format( datetime.now() )

            # Run the workflow. Retry if necessary.
            retry = True
            while( retry ):
                if not run_workflow(
                    config_file = workflow_config.file_path(),
                    target = workflow_config.target().format( run_id = run_id ),
                    root_dir = args.root_dir,
                    forceall = args.forceall,
                    dryrun = args.dryrun,
                    conda_create_envs_only = False,
                    num_cores = workflow_config.num_cores()
                ):
                    print( 'Workflow execution failed. Will retry in {} seconds.' )
                    sleep( args.retry_delay )
                else:
                    retry = False

            # Calculate remeining loop period.
            remaining_period = period - ( datetime.now() - start )

            # Check if workflow execution time exceeded the loop period.
            sleep_period = max( timedelta( 0 ), remaining_period )
            if ( 0 == sleep_period.total_seconds() ):
                print( 'Previous workflow execution time exceeded the loop period.' )

            # Increment loop counter.
            i_loop += 1

            if args.num_loops < 0 or i_loop <= args.num_loops:
                # Notify when the next loop iteration is scheduled.
                str_next = 'Next workflow execution scheduled at: {:%H:%M:%S, %b %d, %Y}'
                print( str_next.format( datetime.now() + sleep_period ) )

                # Sleep until beginning of next loop iteration.
                # See comment at the beginning of this while loop for the reason why time.sleep
                # is being used here (and not a more elegant approach).
                sleep( sleep_period.total_seconds() )


    except Exception as err:

        print( err )
        exit( 100 )



if __name__ == '__main__':
    main()
