"""Fixes for CNRM-CM6-1 model."""
import numpy as np

from ..cmip5.canesm2 import Cl as BaseCl


class Cl(BaseCl):
    """Fixes for ``cl``."""

    def fix_metadata(self, cubes):
        """Fix bounds.

        Parameters
        ----------
        cubes : iris.cube.CubeList
            Input cubes.

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)

        # Vertical coordinates
        for coord_name in ('ap', 'b'):
            coord = cube.coord(var_name=coord_name)
            bounds = coord.bounds
            bounds = np.swapaxes(bounds, 0, 1).reshape(-1, 2)
            coord.bounds = bounds

        # Horizontal coordinates
        for coord_name in ('latitude', 'longitude'):
            cube.coord(coord_name).guess_bounds()
        return cubes
