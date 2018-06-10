import os

PYTHON_SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))
PROJ_ROOT_DIR = os.path.abspath(os.path.join(PYTHON_SCRIPTS_DIR, os.pardir))
SCRATCH_DIR = os.path.join(PROJ_ROOT_DIR, 'scratch')
