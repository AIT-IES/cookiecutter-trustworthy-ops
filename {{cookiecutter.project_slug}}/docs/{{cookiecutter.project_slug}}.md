# {{ cookiecutter.project_name }}

A trustworthy operations workflow.

## About

This package implements a trustworthy operations workflow.
This workflow comprises the following steps:
{%- for item in cookiecutter.workflow_steps.replace(' ','').split(',') | reject('eq','...') %}
 - **Step {{ item }}**: ...
{%- endfor %}

The workflow itself is defined and implemented via the [Snakemake workflow management system](https://snakemake.readthedocs.io).
Snakemake uses the [conda  package management system](https://docs.conda.io/en/latest/) to handle all software dependencies and manage execution environments for all individual steps.
This package provides additional command line scripts to run the workflow, such as storing and retrieving IT credentials (mail account, SOAP API, etc.) or running the workflow periodically.
Furthermore, this package aims at implementing a reasonably secure and trustworthy workflow, see the


## Installation

A secure and trustworthy operations workflow requires a reasonable setup on the host machine.
Therefore, before installing the `{{ cookiecutter.project_slug }}` package, make sure that best practices regarding adminstration, user management and security measures are met on the host machine (see also the platform-specific notes further down below).

After the generation of the workflow from the [template](https://github.com/AIT-IES/cookiecutter-trustworthy-ops), installation of this package and its dependencies is handled via conda.
Consult the official [conda installation instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) to get started with conda.

Create a conda environment for the project and install all dependencies (the command prompt must be in the `{{ cookiecutter.project_slug }}` project root folder):
```bash
conda env create -f environment.yml
```

Activate the environment:
```bash
conda activate {{ cookiecutter.project_slug }}
```


## Usage

### Development / deployment process

In the following, the steps of the intended development / deployment process are explained:

1. **Develop software for individual workflow steps**
   - review software that does not come from trusted sources, to check if it is trustworthy
2. **Freeze development**
   - a file digest is created for relevant files, storing a unique hash (SHA256) based on the file content the file digest is encrypted and protected with a user-defined password
   - see command `{{ cookiecutter.project_slug }}_freeze`
3. **Store confidential data**
   - the credentials cache is encrypted and protected with user-defined password
   - needs to be the same password as used for the file digest
   - see command `{{ cookiecutter.project_slug }}_pwd`
4. **Run the workflow**
   - user provides password for file digest and credentials cache (only at the start when running the workflow periodically)
   - execution is stopped in case the files have been altered w.r.t. the file digest
   - see commands `{{ cookiecutter.project_slug }}_create_envs`, `{{ cookiecutter.project_slug }}_runonce` and `{{ cookiecutter.project_slug }}_loop`


### Workflow definition and configuration

The workflow is specified in the [Snakefile](https://snakemake.readthedocs.io/en/stable/snakefiles/writing_snakefiles.html), which can be found in subfolder [`workflow`](./../workflow).
All steps of the workflow are defined as individual [Snakemake rules](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html).
Each rule executes a Python script (scripts are located in subfolder [`workflow/scripts`](./../workflow/scripts)) in its own conda environment (environment definition files are located in [`workflow/envs`](./../workflow/envs)).

The workflow uses a [configuration file](https://snakemake.readthedocs.io/en/stable/snakefiles/configuration.html), which by default is [`workflow/config.json`](./../workflow/config.json).
The configuration file may contain arbitrary data for configuring the individual workflow steps, but must also contain the following entries:
 - *target*: define the final target of the workflow; uses wildcard *run_id* (string)
 - *run_id_format*: define format string for creating a run-specific ID for each workflow execution based on a [datetime code](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) (string)
 - *credentials*: list of sitenames for which credentials should be stored by the credentials cache (list of string)
 - *num_cores*: number of cores to be used (integer)


### Using confidential data in the workflow

For passing confidential data to the scripts executed in the individual steps, the credentials cache can be used.
IT credentials should be passed to the scripts as parameters (Snakemake keyword [`params`](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html#non-file-parameters-for-rules)) in the [`Snakefile`](./../workflow/Snakefile).
The cache's `retrieve` method returns the username and password for stored sites as tuple.
For example:
```python
rule step1:
    output: 
        'data/step1/{run_id}_step1.out'
    params:
        user = credentials_cache.retrieve( 'https://zenodo.org/' )[0],
        pwd = credentials_cache.retrieve( 'https://zenodo.org/' )[1],
    conda: 
        'envs/step1.yml'
    script: 
        'scripts/step1.py'
```


### Running the default workflow

The following describes how to run the standard configuration of the workflow manually, according to the deployment process described above.
For automating the workflow, also refer to the instructions further down below.

It is assumed that the `{{ cookiecutter.project_slug }}` project root folder is used as working directory.
In case another folder is used as working directory, the (absolute or relative) path to the `{{ cookiecutter.project_slug }}` project root folder needs to be given as input argument to all commands.

After installation, freeze the workflow in order to mark the current state as trustworthy.
When prompted, supply a user-defined passphrase:
```bash
{{ cookiecutter.project_slug }}_freeze
```

Next, provide the required IT credentials for the workflow.
When prompted, use the same passphrase as used for freezing the workflow, then enter username and password for all sites:
```bash
{{ cookiecutter.project_slug }}_pwd
```

Build the conda environments for executing the individual workflow steps.
During the download and installation of these environments, you may be prompted to provide IT credentials (e.g., username / password for accessing a repository):
```bash
{{ cookiecutter.project_slug }}_create_envs
```

To run the whole workflow once, use the following command.
When prompted, provide the previously used passphrase:
```bash
{{ cookiecutter.project_slug }}_runonce
```

To run the whole workflow periodically (by default once a day), use the following command.
Before the workflow is run for the first time, you will be prompted to provide the previously used passphrase:
```bash
{{ cookiecutter.project_slug }}_loop
```


## Reference for command line scripts

### `{{ cookiecutter.project_slug }}_freeze`

Freezes the workflow:
```bash
{{ cookiecutter.project_slug }}_freeze [-h] [-v] [{{ cookiecutter.project_slug | upper }}_DIR]
```

Positional arguments:
 - *{{ cookiecutter.project_slug | upper }}_DIR*: path to `{{ cookiecutter.project_slug }}` project root directory

Optional arguments:
 - *-h*, *--help*: show help message and exit
 - *-v*, *--verbose*: output additional information

### `{{ cookiecutter.project_slug }}_pwd`

Store credentials for workflow:
```bash
{{ cookiecutter.project_slug }}_pwd [-h] [-v] [-n] [--no-freeze] [{{ cookiecutter.project_slug | upper }}_DIR]
```

Positional arguments:
 - *{{ cookiecutter.project_slug | upper }}_DIR*: path to `{{ cookiecutter.project_slug }}` project root directory

Optional arguments:
 - *-h*, *--help*: show help message and exit
 - *-v*, *--verbose*: output additional information
 - *-n*, *--new-cache*: create a new credentials cache
 - *--no-freeze*: do not check if workflow has been frozen

### `{{ cookiecutter.project_slug }}_create_envs`

Create conda environments for all workflow steps:
```bash
{{ cookiecutter.project_slug }}_create-envs [-h] [{{ cookiecutter.project_slug | upper }}_DIR]
```

Positional arguments:
 - *{{ cookiecutter.project_slug | upper }}_DIR*: path to `{{ cookiecutter.project_slug }}` project root directory

Optional arguments:
 - *-h*, *--help*: show help message and exit

### `{{ cookiecutter.project_slug }}_runonce`

Run workflow once:
```bash
{{ cookiecutter.project_slug }}_runonce [-h] [-v] [-f] [-d] [--no-freeze] [--no-cache] [{{ cookiecutter.project_slug | upper }}_DIR]
```

Positional arguments:
 - *{{ cookiecutter.project_slug | upper }}_DIR*: path to `{{ cookiecutter.project_slug }}` project root directory

Optional arguments:
 - *-h*, *--help*: show help message and exit
 - *-v*, *--verbose*: output additional information
 - *-f*, *--forceall*: force all output files to be re-created
 - *-d*, *--dryrun*: only dry-run the workflow
 - *--no-freeze*: do not check if workflow has been frozen
 - *--no-cache*: do not load credentials cache

### `{{ cookiecutter.project_slug }}_loop`

Run workflow periodically, the default period is one day: 
```bash
{{ cookiecutter.project_slug }}_loop [-h] [-v] [-f] [-d] [-N NUM_LOOPS] [-D DAYS] [-H HOURS] [-M MINUTES] [-S SECONDS] [--no-freeze] [--no-cache] [{{ cookiecutter.project_slug | upper }}_DIR]
```
Positional arguments:
 - *{{ cookiecutter.project_slug | upper }}_DIR*: path to `{{ cookiecutter.project_slug }}` project root directory

Optional arguments:
 - *-h*, *--help*: show help message and exit
 - *-v*, *--verbose*: output additional information
 - *-f*, *--forceall*: force all output files to be re-created
 - *-d*, *--dryrun*: only dry-run the workflow
 - *-N NUM_LOOPS*, *--num-loops NUM_LOOPS*: specify maximum number of loops
 - *-D DAYS*, *--days DAYS*: loop period days
 - *-H HOURS*, *--hours HOURS*: loop period hours
 - *-M MINUTES*, *--minutes MINUTES*: loop period minutes
 - *-S SECONDS*, *--seconds SECONDS*: loop period seconds
 - *-r*, *--retry-delay*: delay in seconds for retrying to run a failed workflow execution (default: 60)
 - *--no-freeze*: do not check if workflow has been frozen
 - *--no-cache*: do not load credentials cache


## Unattended workflow execution

Entering a passphrase for running the workflow is not a feasible option when automating the workflow.
For such a case, an environment variable called `{{ cookiecutter.project_slug | upper }}_PWD_FILE` can defined, pointing to a file to which the passphrase has been stored.
When using this option, please **make absolutely sure that the permissions for the passphrase file are set appropriately**, i.e., read access only for the current user!

For instance, on Linux this should look similar to the following:
```bash
echo MY_SUPER_SECURE_PASSPHRASE > .passphrase
chmod 600 .passphrase
export {{ cookiecutter.project_slug | upper }}_PWD_FILE=/path/to/.passphrase
```


## Platform-specific comments

When running the workflow, Snakemake creates temporary files that may contain confidential data in plaintext format.
In the current implementation, file permissions for accessing these temporary depend strongly on the used platform:
- **Linux**: 
  Only the user who started the workflow (via `{{ cookiecutter.project_slug }}_runonce` or `{{ cookiecutter.project_slug }}_loop`) has read access to these temporary files.
  This makes it safe to use `{{ cookiecutter.project_slug }}` in a shared environment (e.g., under `/var`, `/opt` or `/srv`) by more than one user, even if the `{{ cookiecutter.project_slug }}` project root folder is the working directory (default). 
- **Windows**:
  No specific file permissions are applied to the temporary files (Python standard).
  Every user who has read access to the working directory (which contains the temporary files in a subfolder) has also read access to the temporary files.
  When installing `{{ cookiecutter.project_slug }}` in a shared environment, unwanted file access can be avoided by not using the `{{ cookiecutter.project_slug }}` project root folder as working directory, but instead a folder with apropriate access permissions (i.e., no common access, but only access by one user).

**Comment**: Further development could probably fix these differences between Windows and Linux, by using the `pywin32` package to manage folder access permissions.
