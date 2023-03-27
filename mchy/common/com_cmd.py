

class ComCmd:
    """
    Thin wrapper around a string such that debug info can be added if needed in the future
    """

    def __init__(self, cmd: str) -> None:
        self.cmd = cmd
