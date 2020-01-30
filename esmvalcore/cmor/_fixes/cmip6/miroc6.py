"""Fixes for MIROC6 model."""
from ..cmip5.bcc_csm1_1 import Cl as BaseCl


class Cl(BaseCl):
    """Fixes for ``cl``."""

    def fix_metadata(self, cubes):
        """Remove attributes from ``Surface Air Pressure`` coordinate.

        Parameters
        ----------
        cube : iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)
        coord = cube.coord(long_name='Surface Air Pressure')
        coord.attributes = {}
        return cubes
