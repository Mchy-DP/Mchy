

from enum import Enum
from mchy.common.com_logger import ComLogger
from os import path as os_path


class Config():

    class Optimize(Enum):
        NOTHING = 0
        O1 = 1
        O2 = 2
        O3 = 3

    class Verbosity(Enum):
        QUIET = -1
        NORMAL = 0
        VERBOSE = 1
        VV = 2

    DEFAULT_PROJECT_NAME: str = "Project Name"
    DEFAULT_NAMESPACE: str = "prj_ns"
    DEFAULT_RECURSION_LIMIT: int = 32
    DEFAULT_TESTING_COMMENTS: bool = False  # Hidden
    DEFAULT_LOGGER: ComLogger = ComLogger(std_out_level=ComLogger.Level.Info, unique_name="CONFIG-DEFAULT")
    DEFAULT_OUTPUT_PATH: str = os_path.abspath(f"./")
    DEFAULT_DEBUG_MODE: bool = False
    DEFAULT_VERBOSITY: Verbosity = Verbosity.NORMAL
    DEFAULT_OPTIMISATION: Optimize = Optimize.NOTHING
    DEFAULT_DO_BACKUP: bool = True
    DEFAULT_INCLUSION_PATH: str = os_path.abspath(f"./")

    def __init__(
            self,
            project_name: str = DEFAULT_PROJECT_NAME,
            project_namespace: str = DEFAULT_NAMESPACE,
            recursion_limit: int = DEFAULT_RECURSION_LIMIT,
            testing_comments: bool = DEFAULT_TESTING_COMMENTS,
            logger: ComLogger = DEFAULT_LOGGER,
            output_path: str = DEFAULT_OUTPUT_PATH,
            debug_mode: bool = DEFAULT_DEBUG_MODE,
            verbosity: Verbosity = DEFAULT_VERBOSITY,
            optimisation: Optimize = DEFAULT_OPTIMISATION,
            do_backup: bool = DEFAULT_DO_BACKUP,
            inclusion_path: str = DEFAULT_INCLUSION_PATH
            ) -> None:
        self._project_name: str = project_name
        self._project_namespace: str = project_namespace
        self._recursion_limit: int = recursion_limit
        self._testing_comments: bool = testing_comments
        self._logger: ComLogger = logger
        self._output_path: str = output_path
        self._debug_mode: bool = debug_mode
        self._verbosity: Config.Verbosity = verbosity
        self._optimisation: Config.Optimize = optimisation
        self._do_backup: bool = do_backup
        self._inclusion_path: str = inclusion_path

    @property
    def project_name(self) -> str:
        return self._project_name

    @property
    def project_namespace(self) -> str:
        return self._project_namespace

    @property
    def recursion_limit(self) -> int:
        return self._recursion_limit

    @property
    def testing_comments(self) -> bool:
        return self._testing_comments

    @property
    def logger(self) -> ComLogger:
        return self._logger

    @property
    def output_path(self) -> str:
        return self._output_path

    @property
    def debug_mode(self) -> bool:
        return self._debug_mode

    @property
    def verbosity(self) -> Verbosity:
        return self._verbosity

    @property
    def optimisation(self) -> Optimize:
        return self._optimisation

    @property
    def do_backup(self) -> bool:
        return self._do_backup

    @property
    def inclusion_path(self) -> str:
        return self._inclusion_path
