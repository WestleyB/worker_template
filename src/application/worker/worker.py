import asyncio
import copy
import logging
import signal
import typing
import aiotools

from ...domain.entities.web_server_config import WebServerConfig
from ...domain.value_objects.worker_state import WorkerState

logger = logging.getLogger(__name__)


class Worker:
    def __init__(
        self,
        *,
        tasks: typing.List[typing.Callable],
        web_server_config: WebServerConfig = None,
        stop_signal: signal.Signals = signal.SIGINT,
        timeout: float = 0.1,
    ) -> None:
        self.tasks: typing.List[typing.Callable] = tasks
        self.timeout: float = timeout
        self.web_server: typing.Optional[asyncio.AbstractServer] = None
        self._loop: typing.Optional[asyncio.AbstractEventLoop] = None
        self._state: WorkerState = WorkerState.INIT
        self.stop_signal: signal.Signals = stop_signal
        self.web_server_config: WebServerConfig = copy.deepcopy(web_server_config)

        logging.basicConfig(level=logging.DEBUG)

    async def do_init(args) -> None:
        logger.debug(args)

    def run(self, *args, workers: int = 1, **kwargs) -> None:
        """ Public run interface. """

        aiotools.start_server(worker_actxmgr=self.run_worker, num_workers=workers)

    async def _run(self, loop) -> None:
        logger.debug("Running worker...")
        self._set_loop(loop)
        await self.on_start()

        if self.web_server_config is not None:
            await self.start_web_server()

        for task in self.tasks:
            asyncio.ensure_future(task(loop))

        self._state = WorkerState.RUNNING

    @aiotools.server
    async def run_worker(self, loop, pidx, args) -> aiotools.AsyncServerContextManager:
        await self.do_init()
        asyncio.create_task(self._run(loop))

        stop_signal = yield
        await self.stop(stop_signal)

    async def stop(self, stop_signal) -> None:
        if stop_signal == self.stop_signal:
            await self.graceful_shutdown()
        else:
            await self.forced_shutdown()

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def state(self) -> str:
        return self._state.value.name

    def _set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        if self._loop is None:
            self._loop = loop

    async def on_start(self) -> None:
        logger.debug("Starting.....")

    async def _stop(self) -> None:
        """ Set worker state to STOP """

        await asyncio.sleep(2)
        self._state = WorkerState.STOP

    async def on_stop(self) -> None:
        logger.debug("Before Stopping.....")

    async def graceful_shutdown(self) -> None:
        """
        Shutdown the worker:

            1. Execute on_stop
            2. Cancel tasks
            3. Stop web server if server is running
            4. Execute _stop (set worker state to STOP)
        """
        logger.debug("do_graceful_shutdown")
        await self.on_stop()

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

        for task in tasks:
            task.cancel()

        logger.debug(f"Cancelling {len(tasks)} outstanding tasks")

        await self.stop_web_server()
        await self._stop()

    async def forced_shutdown(self) -> None:
        """ Stop webserver if server is running, async tasks are not stopped """

        logger.debug("do_forced_shutdown")
        await self.stop_web_server()
        await self._stop()

    async def start_web_server(self) -> None:
        if self.web_server is None:
            logger.debug("Starting web server")

            self.web_server = await asyncio.start_server(**self.web_server_config.__repr__())

            if self.web_server:
                logger.debug("Web server http://%s:%s is running" % (
                    self.web_server_config.host, self.web_server_config.port))

    async def stop_web_server(self) -> None:
        if self.web_server is not None:
            logger.debug("Stopping web server")
            self.web_server.close()
            await self.web_server.wait_closed()
