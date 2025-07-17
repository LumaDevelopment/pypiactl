class PIAConstants():
    def __init__(self):
        # Options
        self.timeout_flag: str = '-t'
        self.debug_flag: str = '-d'

        # Commands
        self.background_enable_cmd: list[str] = ['background', 'enable']
        self.background_disable_cmd: list[str] = ['background', 'disable']
        self.connect_cmd: list[str] = ['connect']
        self.dedicatedip_add_cmd: list[str] = ['dedicatedip', 'add']
        self.dedicatedip_remove_cmd: list[str] = ['dedicatedip', 'remove']
        self.disconnect_cmd: list[str] = ['disconnect']
        self.get_cmd: list[str] = ['get']
        self.logout_cmd: list[str] = ['logout']
        self.monitor_cmd: list[str] = ['monitor']
        self.reset_settings_cmd: list[str] = ['resetsettings']
        self.version_cmd: list[str] = ['-v']
