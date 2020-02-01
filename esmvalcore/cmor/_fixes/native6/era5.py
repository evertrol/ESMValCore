"""Fixes for ERA5."""
import datetime
import logging

import iris
import numpy as np

from ..fix import Fix
from ..shared import add_scalar_height_coord

logger = logging.getLogger(__name__)


def get_frequency(cube):
    """Determine time frequency of input cube."""
    try:
        time = cube.coord(axis='T')
    except iris.exceptions.CoordinateNotFoundError:
        return 'fx'

    time.convert_units('days since 1850-1-1 00:00:00.0')
    if len(time.points) == 1:
        if cube.long_name != 'Geopotential':
            raise ValueError('Unable to infer frequency of cube '
                             f'with length 1 time dimension: {cube}')
        return 'fx'

    interval = time.points[1] - time.points[0]
    if interval - 1 / 24 < 1e-4:
        return 'hourly'

    return 'monthly'


def fix_invalid_units(cube):
    """Convert m of water equivalent to m."""
    cube.units = 'm'
    return cube


def fix_hourly_time_coordinate(cube):
    """Shift aggregated variables 30 minutes back in time."""
    if get_frequency(cube) == 'hourly':
        time = cube.coord(axis='T')
        time.points = time.points - 1 / 48
        time.guess_bounds()
    return cube


def fix_accumulated_units(cube):
    """Convert accumulations to fluxes."""
    if get_frequency(cube) == 'monthly':
        cube.units = cube.units * 'd-1'
    elif get_frequency(cube) == 'hourly':
        cube.units = cube.units * 'h-1'
    return cube


def multiply_with_density(cube, density=1000):
    """Convert precipitatin from m to kg/m2."""
    cube.data = cube.core_data() * density
    cube.units *= 'kg m**-3'
    return cube


def remove_time_coordinate(cube):
    """Remove time coordinate for invariant parameters."""
    cube = cube[0]
    cube.remove_coord('time')
    return cube


def divide_by_gravity(cube):
    """Convert geopotential to height."""
    cube.units = cube.units / 'm s-2'
    cube.data = cube.core_data() / 9.80665
    return cube


class Evspsbl(Fix):
    """Fixes for evspsbl."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
            fix_accumulated_units(cube)
            multiply_with_density(cube)

        return cubes


class Evspsblpot(Fix):
    """Fixes for evspsblpot."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
            fix_accumulated_units(cube)
            multiply_with_density(cube)

        return cubes


class Mrro(Fix):
    """Fixes for mrro."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
            fix_accumulated_units(cube)
            multiply_with_density(cube)

        return cubes


class Pr(Fix):
    """Fixes for pr."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
            fix_accumulated_units(cube)
            multiply_with_density(cube)

        return cubes


class Prsn(Fix):
    """Fixes for prsn."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            fix_invalid_units(cube)
            fix_hourly_time_coordinate(cube)
            fix_accumulated_units(cube)
            multiply_with_density(cube)

        return cubes


class Orog(Fix):
    """Fixes for orography."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        fixed_cubes = []
        for cube in cubes:
            cube = remove_time_coordinate(cube)
            divide_by_gravity(cube)
            fixed_cubes.append(cube)
        return iris.cube.CubeList(fixed_cubes)


class Rls(Fix):
    """Fixes for Rls."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            cube.attributes['positive'] = 'down'

        return cubes


class Rsds(Fix):
    """Fixes for Rsds."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
            fix_accumulated_units(cube)
            cube.attributes['positive'] = 'down'

        return cubes


class Rsdt(Fix):
    """Fixes for Rsdt."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
            fix_accumulated_units(cube)
            cube.attributes['positive'] = 'down'

        return cubes


class Rss(Fix):
    """Fixes for Rss."""
    def fix_metadata(self, cubes):
        """Fix metadata."""
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
            fix_accumulated_units(cube)
            cube.attributes['positive'] = 'down'

        return cubes


class Tasmax(Fix):
    """Fixes for tasmax."""
    def fix_metadata(self, cubes):
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
        return cubes


class Tasmin(Fix):
    """Fixes for tasmin."""
    def fix_metadata(self, cubes):
        for cube in cubes:
            fix_hourly_time_coordinate(cube)
        return cubes


class AllVars(Fix):
    """Fixes for all variables."""
    def _fix_coordinates(self, cube):
        """Fix coordinates."""
        # Fix coordinate increasing direction
        slices = []
        for coord in cube.coords():
            if coord.var_name in ('latitude', 'pressure_level'):
                slices.append(slice(None, None, -1))
            else:
                slices.append(slice(None))
        cube = cube[tuple(slices)]

        # Add scalar height coordinates
        if 'height2m' in self.vardef.dimensions:
            add_scalar_height_coord(cube, 2.)
        if 'height10m' in self.vardef.dimensions:
            add_scalar_height_coord(cube, 10.)

        for coord_def in self.vardef.coordinates.values():
            axis = coord_def.axis
            coord = cube.coord(axis=axis)
            if axis == 'T':
                coord.convert_units('days since 1850-1-1 00:00:00.0')
            if axis == 'Z':
                coord.convert_units(coord_def.units)
            coord.standard_name = coord_def.standard_name
            coord.var_name = coord_def.out_name
            coord.long_name = coord_def.long_name
            coord.points = coord.core_points().astype('float64')
            if (coord.bounds is None and len(coord.points) > 1
                    and coord_def.must_have_bounds == "yes"):
                coord.guess_bounds()

        self._fix_monthly_time_coord(cube)

        return cube

    def _fix_monthly_time_coord(self, cube):
        """Set the monthly time coordinates to the middle of the month."""
        if get_frequency(cube) == 'monthly':
            coord = cube.coord(axis='T')
            end = []
            for cell in coord.cells():
                month = cell.point.month + 1
                year = cell.point.year
                if month == 13:
                    month = 1
                    year = year + 1
                end.append(cell.point.replace(month=month, year=year))
            end = coord.units.date2num(end)
            start = coord.points
            coord.points = 0.5 * (start + end)
            coord.bounds = np.column_stack([start, end])

    def _fix_units(self, cube):
        """Fix units."""
        cube.convert_units(self.vardef.units)

    def fix_metadata(self, cubes):
        """Fix metadata."""
        fixed_cubes = iris.cube.CubeList()
        for cube in cubes:
            cube.var_name = self.vardef.short_name
            cube.standard_name = self.vardef.standard_name
            cube.long_name = self.vardef.long_name

            cube = self._fix_coordinates(cube)
            self._fix_units(cube)

            cube.data = cube.core_data().astype('float32')
            year = datetime.datetime.now().year
            cube.attributes['comment'] = (
                'Contains modified Copernicus Climate Change '
                f'Service Information {year}')

            fixed_cubes.append(cube)

        return fixed_cubes