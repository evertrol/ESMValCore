"""Fixes for CESM2 model."""
from ..cmip5.bcc_csm1_1 import Cl as BaseCl
from ..fix import Fix
from ..shared import (add_scalar_depth_coord, add_scalar_height_coord,
                      add_scalar_typeland_coord, add_scalar_typesea_coord)


class Cl(BaseCl):
    """Fixes for ``cl``."""


class Fgco2(Fix):
    """Fixes for fgco2."""

    def fix_metadata(self, cubes):
        """Add depth (0m) coordinate.

        Parameters
        ----------
        cube : iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)
        add_scalar_depth_coord(cube)
        return cubes


class Tas(Fix):
    """Fixes for tas."""

    def fix_metadata(self, cubes):
        """Add height (2m) coordinate.

        Parameters
        ----------
        cube : iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)
        add_scalar_height_coord(cube)
        return cubes


class Sftlf(Fix):
    """Fixes for sftlf."""

    def fix_metadata(self, cubes):
        """Add typeland coordinate.

        Parameters
        ----------
        cube : iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)
        add_scalar_typeland_coord(cube)
        return cubes


class Sftof(Fix):
    """Fixes for sftof."""

    def fix_metadata(self, cubes):
        """Add typesea coordinate.

        Parameters
        ----------
        cube : iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)
        add_scalar_typesea_coord(cube)
        return cubes
