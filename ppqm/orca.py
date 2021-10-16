"""
ORCA wrapper functions
"""

import copy
import functools
import logging
import multiprocessing
import os
import pathlib
import shutil
import tempfile
from collections import ChainMap

import numpy as np
from tqdm import tqdm

import rmsd
from ppqm import chembridge, constants, env, linesio, misc, shell, units
from ppqm.calculator import BaseCalculator

ORCA_CMD = "orca"
ORCA_FILENAME = "_tmp_orca_input.inp"
ORCA_FILES = ["_tmp_orca_input.gbw", "_tmp_orca_input.out", "_tmp_orca_input.prop"]

COLUMN_ENERGY = "total_energy"
COLUMN_COORD = "coord"
COLUMN_ATOMS = "atoms"
COLUMN_GSOLV = "gsolv"
COLUMN_DIPOLE = "dipole"
COLUMN_CONVERGED = "is_converged"
COLUMN_STEPS = "opt_steps"

_logger = logging.getLogger("orca")

class OrcaCalculator(BaseCalculator):
    """Orca wrapper

    This class should not be used directly, use a class appropriate for your
    quantum calculations (e.g. MopacCalculator or GamessCalculator) instead.
    """

    def health_check(self):

        assert env.which(self.cmd), f"Cannot find {self.cmd}"

        stdout, stderr = shell.execute(f"{self.cmd} --version")

        try:
            stdout = stdout.split("\n")
            stdout = [x for x in stdout if "*" in x]
            version = stdout[0].strip()
            version = version.split()
            version = version[3]
            version = version.split(".")
            major, minor, patch = version
        except Exception:
            assert False, "too old xtb version"

        assert int(major) >= 6, "too old xtb version"
        assert int(minor) >= 4, "too old xtb version"