

class ComCmd:
    """
    Thin wrapper around a string such that debug info can be added if needed in the future
    must NOT implement __eq__
    """

    def __init__(self, cmd: str) -> None:
        self.cmd = cmd
