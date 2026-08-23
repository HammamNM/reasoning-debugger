from kernel.runtime import KernelRuntime
from kernel.session import KernelSession


class GenericKernelBootstrap:

    def create_runtime(self):

        session = KernelSession()

        runtime = KernelRuntime(
            session
        )

        runtime.initialize()

        return runtime


