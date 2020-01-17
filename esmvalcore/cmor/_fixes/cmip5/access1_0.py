"""Fixes for the ACCESS1-0 model."""

import iris
from cf_units import Unit

from ..fix import Fix


# noinspection PyPep8
class AllVars(Fix):
    """Common fixes to all vars."""

    def fix_metadata(self, cubes):
        """
        Fix metadata.

        Fixes wrong calendar 'gregorian' instead of 'proleptic_gregorian'

        Parameters
        ----------
        cube: iris.cube.Cube

        Returns
        -------
        iris.cube.Cube

        """
        for cube in cubes:
            try:
                time = cube.coord('time')
            except iris.exceptions.CoordinateNotFoundError:
                continue
            else:
                time.units = Unit(time.units.name, 'gregorian')
        return cubes


class Cl(Fix):
    """Fixes for ``cl``."""

    def fix_metadata(self, cubes):
        """Remove attributes from ``vertical coordinate formula term: b(k)``.

        Parameters
        ----------
        cube : iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)
        coord = cube.coord(long_name='vertical coordinate formula term: b(k)')
        coord.attributes = {}
        return cubes
