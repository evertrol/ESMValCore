"""
Provides testing capabilities for :mod:`esmvaltool` package.

"""
import unittest
from functools import wraps
from unittest import mock

import numpy as np


class Test(unittest.TestCase):
    """
    Provides esmvaltool specific testing functionality.

    """

    def _remove_testcase_patches(self):
        """
        Helper method to remove per-testcase patches installed by
        :meth:`patch`.

        """
        # Remove all patches made, ignoring errors.
        for patch in self.testcase_patches:
            patch.stop()

        # Reset per-test patch control variable.
        self.testcase_patches.clear()

    def patch(self, *args, **kwargs):
        """
        Install a patch to be removed automatically after the current test.

        The patch is created with :func:`mock.patch`.

        Parameters
        ----------
        args : list
            The parameters to be passed to :func:`mock.patch`.
        kwargs : dict
            The keyword parameters to be passed to :func:`mock.patch`.

        Returns
        -------
            The substitute mock instance returned by :func:`patch.start`.

        """
        # Make the new patch and start it.
        patch = mock.patch(*args, **kwargs)
        start_result = patch.start()

        # Create the per-testcases control variable if it does not exist.
        # NOTE: this mimics a setUp method, but continues to work when a
        # subclass defines its own setUp.
        if not hasattr(self, 'testcase_patches'):
            self.testcase_patches = {}

        # When installing the first patch, schedule remove-all at cleanup.
        if not self.testcase_patches:
            self.addCleanup(self._remove_testcase_patches)

        # Record the new patch and start object for reference.
        self.testcase_patches[patch] = start_result

        # Return patch replacement object.
        return start_result

    @wraps(np.testing.assert_array_equal)
    def assert_array_equal(self, a, b):
        np.testing.assert_array_equal(a, b)
        if np.ma.isMaskedArray(a) or np.ma.isMaskedArray(b):
            np.testing.assert_array_equal(a.mask, b.mask)
