"""Fixes for CNRM-CM6-1 model."""
from ..cmip5.canesm2 import Cl as BaseCl


class Cl(BaseCl):
    """Fixes for ``cl``."""

    def fix_metadata(self, cubes):
        """Add bounds for latitude and longitude.

        Parameters
        ----------
        cube : iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)
        for coord_name in ('latitude', 'longitude'):
            cube.coord(coord_name).guess_bounds()
        return cubes
