# Pre-Generate Hook
#
# This hook checks the validity of some of the template
# arguments.

import sys
import re
from functools import partial


# Regex object for URI sanity check.
URI_REGEX = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # ... localhost ...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ... or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)


# Regex object for mail address sanity check.
MAIL_ADDRESS_REGEX = re.compile(
    r'^[A-Z0-9\.\+_-]+@[A-Z0-9\._-]+\.[A-Z]*$',
    re.IGNORECASE
)


# Regex object for Snakemake rule names sanity check.
RULE_REGEX =  re.compile(
    r'^[^\d\W]\w*\Z',
    re.UNICODE
)


# Generic helper function for sanity check.
def check( items, validators, err ):
    ok = True
    for i in items:
        if not any( [ f( i ) for f in validators ] ):
            print( err.format( i ) )
            ok = False
    return ok


# Retrieve sanitized list from template string.
def get_sanitized_list( ckstr ):

    # Remove whitespace and split into list.
    cklist = ckstr.replace( ' ', '' ).split( ',' )

    # Pop last item if it is just an ellipsis (...).
    if '...' in cklist[-1:]: cklist.pop()

    return cklist


# Validate string expression against regex object.
def validate_expression( regex, expr ):
    return ( regex.fullmatch( expr ) is not None )


# Check template variables.
def check_template_variables():

    # Sanity check of workflow step names.
    check_workflow_steps = check(
        items = get_sanitized_list(
            '{{ cookiecutter.workflow_steps }}'
        ),
        validators = [
            partial( validate_expression, RULE_REGEX ),
        ],
        err = 'Invalid name for workflow step: {}'
    )


    # Sanity check of mail addresses / sitenames.
    check_credentials = check(
        items = get_sanitized_list(
            '{{ cookiecutter.credentials }}'
        ),
        validators = [
            partial( validate_expression, MAIL_ADDRESS_REGEX ),
            partial( validate_expression, URI_REGEX ),
        ],
        err = 'Invalid sitename / mail address: {}'
    )

    return all( [ check_workflow_steps, check_credentials ] )


if __name__ == '__main__':
    if not check_template_variables():
        sys.exit( 1 )