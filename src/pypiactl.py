from ._config import PIAConfig

class PIA():
    def __init__(
        self,
        config: PIAConfig=PIAConfig()
    ):
        self.config = config