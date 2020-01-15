"""Derivation of variable ``mblc_fraction``."""

import dask.array as da
import iris
import iris.coord_categorisation

from .._regrid import extract_levels
from ._baseclass import DerivedVariableBase
from ._shared import var_name_constraint

LAT_CONSTRAINT = iris.Constraint(
    latitude=lambda c: -40.0 <= c <= -20.0 or 20.0 <= c <= 40.0)
OMEGA_LEVEL = 50000.0
UPPER_LIMIT_LEVEL = 70000.0


def _total_cl_fraction(cl_cube, limit):
    """Compute total cloud cover below a certain ``limit`` pressure level."""
    levs = cl_cube.coord('air_pressure').core_points()

    # Mask cubes below certain height level
    mask = da.where(levs >= limit, False, True)
    cl_cube.data = da.ma.masked_array(cl_cube.core_data(), mask=mask)
    inv_cl_cube = cl_cube.copy(data=1.0 - cl_cube.core_data() / 100.0)

    # Total cloud fraction (random overlap assumption)
    for coord in inv_cl_cube.coords(dim_coords=True):
        if iris.util.guess_coord_axis(coord) == 'Z':
            z_coord = coord
            break
    else:
        raise ValueError(f"Cannot determine height axis (Z) of cube "
                         f"{cl_cube.summary(shorten=True)}")
    z_idx = inv_cl_cube.coord_dims(z_coord)[0]
    total_cl = (1.0 - inv_cl_cube.core_data().prod(axis=z_idx)) * 100.0
    clt_cube = inv_cl_cube.collapsed(z_coord, iris.analysis.MEAN)  # dummy
    clt_cube.data = total_cl
    clt_cube.var_name = 'clt'
    clt_cube.standard_name = 'cloud_area_fraction'
    clt_cube.long_name = 'Total Cloud Fraction'
    clt_cube.cell_methods = clt_cube.cell_methods[:-1]
    return clt_cube


class DerivedVariable(DerivedVariableBase):
    """Derivation of variable `mblc_fraction`."""

    @staticmethod
    def required(project):
        """Declare the variables needed for derivation."""
        required = [
            {
                'short_name': 'wap'
            },
            {
                'short_name': 'cl'
            },
        ]
        return required

    @staticmethod
    def calculate(cubes):
        """Compute evapotranspiration."""
        cl_cube = cubes.extract_strict(
            var_name_constraint('cl') & LAT_CONSTRAINT)
        wap_cube = cubes.extract_strict(
            var_name_constraint('wap') & LAT_CONSTRAINT)

        # Calculate total cloud area fraction below 700 hPa
        mblc_cube = _total_cl_fraction(cl_cube, UPPER_LIMIT_LEVEL)
        print(mblc_cube)

        # Extract 500 hPa level of wap
        wap_cube = extract_levels(wap_cube, OMEGA_LEVEL, 'linear')

        # Get monthly climatologies
        # TODO: Remove when bug in iris is fixed
        for aux_factory in mblc_cube.aux_factories:
            mblc_cube.remove_aux_factory(aux_factory)
        iris.coord_categorisation.add_month_number(mblc_cube, 'time')
        iris.coord_categorisation.add_month_number(wap_cube, 'time')
        mblc_cube = mblc_cube.aggregated_by('month_number', iris.analysis.MEAN)
        wap_cube = wap_cube.aggregated_by('month_number', iris.analysis.MEAN)

        # Mask subsidence regions (positive wap at 500 hPa)
        mask = da.where(wap_cube.data > 0, False, True)

        # Get total MBLC fraction
        mblc_cube.data = da.ma.masked_array(mblc_cube.core_data(), mask=mask)
        area_weights = iris.analysis.cartography.area_weights(mblc_cube)
        mblc_cube = mblc_cube.collapsed(['latitude', 'longitude'],
                                        iris.analysis.MEAN,
                                        weights=area_weights)
        return mblc_cube
