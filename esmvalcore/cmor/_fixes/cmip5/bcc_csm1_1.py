"""Fixes for bcc-csm1-1."""
from shutil import copyfile

import netCDF4 as nc
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.ndimage import map_coordinates

from ..fix import Fix


class Cl(Fix):
    """Fixes for cl."""

    def fix_file(self, filepath, output_dir):
        """Fix file.

        Fix file so that :mod:`iris` correctly reads bounds of
        ``'atmosphere_hybrid_sigma_pressure_coordinate'`` coordinate.

        Parameters
        ----------
        filepath : str
            Input file.
        output_dir : str
            Output directory of new file.

        Returns
        -------
        str
            Path to new file.

        """
        new_path = self.get_fixed_filepath(output_dir, filepath)
        copyfile(filepath, new_path)
        dataset = nc.Dataset(new_path, mode='a')
        lev_var = dataset.variables['lev']
        lev_var.standard_name = 'atmosphere_hybrid_sigma_pressure_coordinate'
        lev_var.formula_terms = 'p0: p0 a: a b: b ps: ps'
        for bounds in ('bnds', 'bounds'):
            if (f'a_{bounds}' in dataset.variables and
                    f'b_{bounds}' in dataset.variables):
                a_bnds = f'a_{bounds}'
                b_bnds = f'b_{bounds}'
                break
        else:
            raise ValueError("No bounds for 'a' and 'b' found")
        dataset.variables['a'].bounds = a_bnds
        dataset.variables['b'].bounds = b_bnds
        for bounds in ('bnds', 'bounds'):
            if f'lev_{bounds}' in dataset.variables:
                dataset.variables[f'lev_{bounds}'].formula_terms = (
                    f'p0: p0 a: {a_bnds} b: {b_bnds} ps: ps')
            break
        else:
            raise ValueError("No bounds for 'lev' found")
        dataset.close()
        return new_path


class Tos(Fix):
    """Fixes for tos."""

    def fix_data(self, cube):
        """Fix data.

        Calculate missing latitude/longitude boundaries using interpolation.

        Parameters
        ----------
        cube: iris.cube.Cube

        Returns
        -------
        iris.cube.Cube

        """
        rlat = cube.coord('grid_latitude').points
        rlon = cube.coord('grid_longitude').points

        # Transform grid latitude/longitude to array indices [0, 1, 2, ...]
        rlat_to_idx = InterpolatedUnivariateSpline(
            rlat, np.arange(len(rlat)), k=1)
        rlon_to_idx = InterpolatedUnivariateSpline(
            rlon, np.arange(len(rlon)), k=1)
        rlat_idx_bnds = rlat_to_idx(cube.coord('grid_latitude').bounds)
        rlon_idx_bnds = rlon_to_idx(cube.coord('grid_longitude').bounds)

        # Calculate latitude/longitude vertices by interpolation
        lat_vertices = []
        lon_vertices = []
        for (i, j) in [(0, 0), (0, 1), (1, 1), (1, 0)]:
            (rlat_v, rlon_v) = np.meshgrid(
                rlat_idx_bnds[:, i], rlon_idx_bnds[:, j], indexing='ij')
            lat_vertices.append(
                map_coordinates(
                    cube.coord('latitude').points, [rlat_v, rlon_v],
                    mode='nearest'))
            lon_vertices.append(
                map_coordinates(
                    cube.coord('longitude').points, [rlat_v, rlon_v],
                    mode='wrap'))
        lat_vertices = np.array(lat_vertices)
        lon_vertices = np.array(lon_vertices)
        lat_vertices = np.moveaxis(lat_vertices, 0, -1)
        lon_vertices = np.moveaxis(lon_vertices, 0, -1)

        # Copy vertices to cube
        cube.coord('latitude').bounds = lat_vertices
        cube.coord('longitude').bounds = lon_vertices

        return cube
