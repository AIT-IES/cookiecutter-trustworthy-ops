from setuptools import setup, find_packages

with open( './docs/{{ cookiecutter.project_slug }}.md', 'r' ) as f:
    long_description = f.read()

setup(
    name = '{{ cookiecutter.project_slug }}',
    version = '0.1',
    description = 'A trustworthy operations workflow',
    long_description = long_description,

    #maintainer = '',
    #maintainer_email = '',
    #url = '',
    #license = '',
    #keywords = [],
    #classifiers = [],

    platforms = [ 'any' ],
    packages = find_packages(),
    install_requires = [
        'snakemake',
        'pycryptodome>=3.9.7',
    ],
    entry_points={
        'console_scripts': [
            '{{ cookiecutter.project_slug }}_create_envs = {{ cookiecutter.project_slug }}.cli.create_envs:main',
            '{{ cookiecutter.project_slug }}_freeze = {{ cookiecutter.project_slug }}.cli.freeze:main',
            '{{ cookiecutter.project_slug }}_pwd = {{ cookiecutter.project_slug }}.cli.pwd:main',
            '{{ cookiecutter.project_slug }}_runonce = {{ cookiecutter.project_slug }}.cli.runonce:main',
            '{{ cookiecutter.project_slug }}_loop = {{ cookiecutter.project_slug }}.cli.loop:main',
        ]
    },
)
