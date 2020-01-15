"""Fixes for MIROC6 model."""
from ..fix import Fix


class Cl(Fix):
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
        coord = cube.coord('Surface Air Pressure')
        coord.attributes = {}
        return cubes
