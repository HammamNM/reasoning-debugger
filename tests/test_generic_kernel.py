import unittest

from kernel.generic_bootstrap import GenericKernelBootstrap
from kernel.session import KernelSession
from kernel.runtime import KernelRuntime


class TestGenericKernel(unittest.TestCase):

    def test_create_generic_runtime(self):

        runtime = GenericKernelBootstrap().create_runtime()

        self.assertIsInstance(
            runtime,
            KernelRuntime
        )

        self.assertIsInstance(
            runtime.session,
            KernelSession
        )

        self.assertEqual(
            runtime.session.scenario_id,
            ""
        )


if __name__ == "__main__":
    unittest.main()
