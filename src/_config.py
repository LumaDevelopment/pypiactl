# Library configuration object

class PIAConfig():
    def __init__(
        self,
        executable_path: str = 'piactl'
    ):
        self.executable_path = executable_path