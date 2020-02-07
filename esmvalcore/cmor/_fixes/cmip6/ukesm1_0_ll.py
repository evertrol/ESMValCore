"""Fixes for CMIP6 UKESM1-0-LL."""
import iris

from ..fix import Fix
from ..shared import ALTITUDE_TO_PRESSURE, fix_bounds
from .hadgem3_gc31_ll import AllVars as BaseAllVars


class AllVars(BaseAllVars):
    """Fixes for all vars."""


class Cl(Fix):
    """Fixes for ``'cl'``."""

    def fix_metadata(self, cubes):
        """Fix hybrid sigma height coordinate and add pressure levels.

        Parameters
        ----------
        cubes : iris.cube.CubeList
            Input cubes which need to be fixed.

        Returns
        -------
        iris.cube.CubeList

        """
        cl_cube = self.get_cube_from_list(cubes)

        # Remove all existing aux_factories
        for aux_factory in cl_cube.aux_factories:
            cl_cube.remove_aux_factory(aux_factory)

        # Fix bounds
        fix_bounds(cl_cube, cubes, ('lev', 'b'))

        # Add aux_factory again
        height_coord_factory = iris.aux_factory.HybridHeightFactory(
            delta=cl_cube.coord(var_name='lev'),
            sigma=cl_cube.coord(var_name='b'),
            orography=cl_cube.coord(var_name='orog'),
        )
        cl_cube.add_aux_factory(height_coord_factory)

        # Add pressure level coordinate
        height_coord = cl_cube.coord('altitude')
        if height_coord.units != 'm':
            height_coord.convert_units('m')
        pressure_points = ALTITUDE_TO_PRESSURE(height_coord.core_points())
        pressure_bounds = ALTITUDE_TO_PRESSURE(height_coord.core_bounds())
        pressure_coord = iris.coords.AuxCoord(pressure_points,
                                              bounds=pressure_bounds,
                                              var_name='plev',
                                              standard_name='air_pressure',
                                              long_name='pressure',
                                              units='Pa')
        cl_cube.add_aux_coord(pressure_coord, cl_cube.coord_dims(height_coord))

        return iris.cube.CubeList([cl_cube])
