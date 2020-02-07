"""Fixes for CNRM-CM6-1 model."""
import iris

from esmvalcore.preprocessor._derive._shared import var_name_constraint

from ..cmip5.bcc_csm1_1 import Cl as BaseCl
from ..shared import cube_to_aux_coord, get_bounds_cube


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

        # Fix vertical coordinate points
        for coord_name in ('ap', 'b', 'ps'):
            coord_cube = cubes.extract_strict(var_name_constraint(coord_name))
            aux_coord = cube_to_aux_coord(coord_cube)
            if coord_name == 'ap':
                aux_coord.units = 'Pa'
            if coord_name == 'ps':
                cube.add_aux_coord(aux_coord, (0, 2, 3))
            else:
                cube.add_aux_coord(aux_coord, 1)
            cubes.remove(coord_cube)

        # Fix vertical coordinate bounds
        for coord_name in ('ap', 'b'):
            bounds_cube = get_bounds_cube(cubes, coord_name)
            bounds = bounds_cube.data.reshape(-1, 2)
            new_bounds_cube = iris.cube.Cube(bounds,
                                             **bounds_cube.metadata._asdict())
            cubes.remove(bounds_cube)
            cubes.append(new_bounds_cube)

        # Fix hybrid sigma pressure coordinate
        cubes = super().fix_metadata(cubes)

        # Fix horizontal coordinates bounds
        for coord_name in ('latitude', 'longitude'):
            cube.coord(coord_name).guess_bounds()
        return cubes
