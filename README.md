# cookiecutter-trustworthy-ops

A template for trustworthy operations workflows.

## About

This project provides a template ([cookiecutter](https://cookiecutter.readthedocs.io/en/latest/README.html)) for trustworthy operations workflows.
The workflow itself is defined and implemented via the [Snakemake workflow management system](https://snakemake.readthedocs.io).
Snakemake uses the [conda  package management system](https://docs.conda.io/en/latest/) to handle all software dependencies and manage execution environments for all individual steps.
The generated package provides additional command line scripts to run the workflow, such as storing and retrieving IT credentials (mail account, SOAP API, etc.) or running the workflow periodically.
Furthermore, the generated package aims at implementing a reasonably secure and trustworthy workflow, see the


## A few words about Security

**Requirement**:
- It must be possible to use *confidential data* (IT credentials) in the workflow, such as the username and password for mails accounts or the credentials for REST APIs.

**Challenges**:
- We want to use a *semi-open IT environment*, where several people have access.
  For instance, more than one person should be able to restart the periodic execution in case of updates or technical problems.
- We want to follow an agile development process using Python, because it is very efficient and convenient, but this also opens up many possibilities for *malicious hacking*.
  For instance, it is easy to find out what countermeasures are in place and how to circumvent or reverse them.
- Nevertheless, we must ensure a *reasonably secure workflow*, because this is essential for a good and trustful collaboration with our project partners (and our own IT division)

**Solution**:
- A secure workflow in a strict sense is not possible with an approach based on Python and Snakemake.
  However, we can aim at the next better thing, which is a *trustworthy workflow*.
- This means we try to use security measures wherever possible, e.g., encryption of sensitive data and adequate user management and file permissions on the deployed host.
- And we use *trustworthy software* everywhere else, i.e., software where there is no reason to assume that it has been (intentionally) compromised.
  To this end, we use software from trusted sources by defining the environments for the overall workflow and individual steps via conda environments (supported by Snakemake).
  On top of that, this package enables a transparent and reproducible development / deployment process for additional software provided by the user (i.e., scripts for individual workflow steps)


## Workflow development / deployment process

In the following, the intended development / deployment process for the generated workflow is explained:

1. **Develop software for individual workflow steps**
   - review software that does not come from trusted sources, to check if it is trustworthy
2. **Freeze development**
   - a file digest is created for relevant files, storing a unique hash (SHA256) based on the file content the file digest is encrypted and protected with a user-defined password
3. **Store confidential data**
   - the credentials cache is encrypted and protected with user-defined password
   - needs to be the same password as used for the file digest
4. **Run the workflow**
   - user provides password for file digest and credentials cache (only at the start when running the workflow periodically)
   - execution is stopped in case the files have been altered w.r.t. the file digest

Instructions for this development / deployment process (e.g., usage of shell scripts) are provided in subfolder `docs` of the generated workflow (HTML and Markdown).


## Use the template to generate a workflow

Install [cookiecutter](https://github.com/cookiecutter/cookiecutter):
```bash
pip install cookiecutter
```

Use cookiecutter to generate a skeleton of your workflow, following the prompts to fill in your specific information (see explanation below):
```bash
cookiecutter https://github.com/AIT-IES/cookiecutter-trustworthy-ops
```

At the start of the generation process, you will be asked to provide the following information:
- **project_name**: name of your workflow
- **project_slug**: slug of your workflow, i.e., a version of the workflow that can be used as Python package name or URL
- **workflow_steps**: comma-separated list of the names of the steps of your workflow
- **credentials**: comma-separated list of sitenames and/or mail addresses for which IT credentials shoud be stored for your workflow


## Workflow adaptation

Based on the provided information, a dummy workflow with reasonable defaults will be generated.
However, to make it really usable for your own purpose, you have to adapt the generated workflow.

### Workflow definition

The workflow is specified in the [Snakefile](https://snakemake.readthedocs.io/en/stable/snakefiles/writing_snakefiles.html), which can be found in subfolder `workflow`.
All steps of the workflow are defined as individual [Snakemake rules](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html).

### Workflow scripts and environments

Each rule executes a Python script (scripts are located in subfolder `workflow/scripts`) in its own conda environment (environment definition files are located in `workflow/envs`).

### Workflow configuration

The workflow uses a [configuration file](https://snakemake.readthedocs.io/en/stable/snakefiles/configuration.html), which by default is `workflow/config.json`.
The configuration file may contain arbitrary data for configuring the individual workflow steps, but must also contain the following entries:
 - *target*: define the final target of the workflow; uses wildcard *run_id* (string)
 - *run_id_format*: define format string for creating a run-specific ID for each workflow execution based on a [datetime code](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) (string)
 - *credentials*: list of sitenames for which credentials should be stored by the credentials cache (list of string)
 - *num_cores*: number of cores to be used (integer)

### Workflow documentation

A documentation draft with the most important instructions (e.g., usage of shell scripts) is provided in subfolder `docs` of the generated workflow (HTML and Markdown).
However, for a proper documentation this should be updated to reflect the specific details of your own workflow.

### Python Distutils setup

In case you want to publish your workflow, e.g., via the [Python Package Index (PyPI)](https://pypi.org/), you need to provide the missing attributes in file `setup.py` (*maintainer*, *maintainer_email*, *url*, *license*, *keywords* and *classifiers*).
