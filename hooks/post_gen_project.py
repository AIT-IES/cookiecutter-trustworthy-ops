# Post-Generate Hook
#
# This hook creates additional files (dummy environment
# file, dummy workflow scripts) by copying a default 
# file (no template substitution inside the files).

import sys
from pathlib import Path
from shutil import copyfile


# Retrieve sanitized list from template string.
def get_sanitized_list( ckstr ):

    # Remove whitespace and split into list.
    cklist = ckstr.replace( ' ', '' ).split( ',' )

    # Pop last item if it is just an ellipsis (...).
    if '...' in cklist[-1:]: cklist.pop()

    return cklist


# Helper function for copying default files.
def copy_files( items, path, default_file, file_extension ):
    src = Path( path, default_file )
    for i in items:
        dst = Path( path, i + file_extension )
        copyfile( src, dst )


# Copy all additional files.
def copy_all_files():

    try:
        # Create dummy environment files for all workflow steps.
        copy_files(
            items = get_sanitized_list(
                '{{ cookiecutter.workflow_steps }}'
            ),
            path = Path( '.', 'workflow', 'envs' ),
            default_file = 'default.yml',
            file_extension = '.yml'
        )

        # Create dummy scripts for all workflow steps.
        copy_files(
            items = get_sanitized_list(
                '{{ cookiecutter.workflow_steps }}'
            ),
            path = Path( '.', 'workflow', 'scripts' ),
            default_file = 'default.py',
            file_extension = '.py'
        )
    except:
        return False

    return True


if __name__ == '__main__':
    if not copy_all_files():
        sys.exit( 1 )