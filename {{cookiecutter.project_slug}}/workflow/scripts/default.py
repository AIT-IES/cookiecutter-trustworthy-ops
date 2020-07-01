from pathlib import Path


def main( output_file_name ):

    # Write dummy output file.
    Path( output_file_name ).touch()


if __name__ == '__main__':

    main(
        output_file_name = snakemake.output[0]
    )
