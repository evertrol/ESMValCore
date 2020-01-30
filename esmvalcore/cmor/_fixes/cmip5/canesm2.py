"""Fixes for CanESM2 model."""
from shutil import copyfile

import netCDF4 as nc

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
        lev_var.formula_terms = 'ap: ap b: b ps: ps'
        for bounds in ('bnds', 'bounds'):
            if (f'ap_{bounds}' in dataset.variables and
                    f'b_{bounds}' in dataset.variables):
                ap_bnds = f'ap_{bounds}'
                b_bnds = f'b_{bounds}'
                break
        else:
            raise ValueError("No bounds for 'ap' and 'b' found")
        ap_var = dataset.variables['ap']
        if 'units' not in ap_var.ncattrs():
            ap_var.units = 'Pa'
        ap_var.bounds = ap_bnds
        dataset.variables['b'].bounds = b_bnds
        for bounds in ('bnds', 'bounds'):
            if f'lev_{bounds}' in dataset.variables:
                dataset.variables[f'lev_{bounds}'].formula_terms = (
                    f'ap: {ap_bnds} b: {b_bnds} ps: ps')
            break
        else:
            raise ValueError("No bounds for 'lev' found")
        dataset.close()
        return new_path


class FgCo2(Fix):
    """Fixes for fgco2."""

    def fix_data(self, cube):
        """
        Fix data.

        Fixes discrepancy between declared units and real units

        Parameters
        ----------
        cube: iris.cube.Cube

        Returns
        -------
        iris.cube.Cube

        """
        metadata = cube.metadata
        cube *= 12.0 / 44.0
        cube.metadata = metadata
        return cube
