"""Shared functions for fixes."""
import logging
import os

import dask.array as da
import iris
import pandas as pd
from cf_units import Unit
from scipy.interpolate import interp1d

from esmvalcore.preprocessor._derive._shared import var_name_constraint

logger = logging.getLogger(__name__)


def _get_altitude_to_pressure_func():
    """Get function converting altitude [m] to air pressure [Pa]."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(base_dir, 'us_standard_atmosphere.csv')
    data_frame = pd.read_csv(source_file, comment='#')
    func = interp1d(data_frame['Altitude [m]'],
                    data_frame['Pressure [Pa]'],
                    kind='cubic',
                    fill_value='extrapolate')
    return func


ALTITUDE_TO_PRESSURE = _get_altitude_to_pressure_func()


def add_scalar_depth_coord(cube, depth=0.0):
    """Add scalar coordinate 'depth' with value of `depth`m."""
    logger.debug("Adding depth coordinate (%sm)", depth)
    depth_coord = iris.coords.AuxCoord(depth,
                                       var_name='depth',
                                       standard_name='depth',
                                       long_name='depth',
                                       units=Unit('m'),
                                       attributes={'positive': 'down'})
    try:
        cube.coord('depth')
    except iris.exceptions.CoordinateNotFoundError:
        cube.add_aux_coord(depth_coord, ())
    return cube


def add_scalar_height_coord(cube, height=2.0):
    """Add scalar coordinate 'height' with value of `height`m."""
    logger.debug("Adding height coordinate (%sm)", height)
    height_coord = iris.coords.AuxCoord(height,
                                        var_name='height',
                                        standard_name='height',
                                        long_name='height',
                                        units=Unit('m'),
                                        attributes={'positive': 'up'})
    try:
        cube.coord('height')
    except iris.exceptions.CoordinateNotFoundError:
        cube.add_aux_coord(height_coord, ())
    return cube


def add_scalar_typeland_coord(cube, value='default'):
    """Add scalar coordinate 'typeland' with value of `value`."""
    logger.debug("Adding typeland coordinate (%s)", value)
    typeland_coord = iris.coords.AuxCoord(value,
                                          var_name='type',
                                          standard_name='area_type',
                                          long_name='Land area type',
                                          units=Unit('no unit'))
    try:
        cube.coord('area_type')
    except iris.exceptions.CoordinateNotFoundError:
        cube.add_aux_coord(typeland_coord, ())
    return cube


def add_scalar_typesea_coord(cube, value='default'):
    """Add scalar coordinate 'typesea' with value of `value`."""
    logger.debug("Adding typesea coordinate (%s)", value)
    typesea_coord = iris.coords.AuxCoord(value,
                                         var_name='type',
                                         standard_name='area_type',
                                         long_name='Ocean area type',
                                         units=Unit('no unit'))
    try:
        cube.coord('area_type')
    except iris.exceptions.CoordinateNotFoundError:
        cube.add_aux_coord(typesea_coord, ())
    return cube


def cube_to_aux_coord(cube):
    """Convert :class:`iris.cube.Cube` to :class:`iris.coords.AuxCoord`."""
    aux_coord = iris.coords.AuxCoord(cube.core_data(),
                                     var_name=cube.var_name,
                                     standard_name=cube.standard_name,
                                     long_name=cube.long_name,
                                     units=cube.units)
    return aux_coord


def get_bounds_cube(cubes, coord_var_name):
    """Find bound cube for a given variable in a list of cubes."""
    for bounds in ('bnds', 'bounds'):
        bound_var = f'{coord_var_name}_{bounds}'
        cube = cubes.extract(var_name_constraint(bound_var))
        if len(cube) == 1:
            return cube[0]
        if len(cube) > 1:
            raise ValueError(
                f"Multiple cubes with var_name '{bound_var}' found")
    raise ValueError(
        f"No bounds for coordinate variable '{coord_var_name}' available in "
        f"cubes\n{cubes}")


def fix_bounds(cube, cubes, coord_var_names):
    """Fix bounds for cube that could not be read correctly by :mod:`iris`."""
    for coord_var_name in coord_var_names:
        coord = cube.coord(var_name=coord_var_name)
        if coord.bounds is not None:
            continue
        bounds_cube = get_bounds_cube(cubes, coord_var_name)
        cube.coord(var_name=coord_var_name).bounds = bounds_cube.core_data()
        logger.debug("Fixed bounds of coordinate '%s'", coord_var_name)


def round_coordinates(cubes, decimals=5):
    """Round all dimensional coordinates of all cubes."""
    for cube in cubes:
        for coord in cube.coords(dim_coords=True):
            coord.points = da.round(da.asarray(coord.core_points()), decimals)
            if coord.bounds is not None:
                coord.bounds = da.round(da.asarray(coord.core_bounds()),
                                        decimals)
    return cubes
