# PIA Background Activity Controller

class PIABackground():
    def __init__(self, pia):
        self._pia = pia

    def enable(
        self,
        timeout_in_s: None | int = None, 
        debug_option: bool = False
    ) -> str:
        """
        Keeps the PIA daemon running even if the GUI 
        client is closed or has not been started.
        \n
        Returns the output of the command.
        """
        return self._pia._exec_one_shot_cmd(
            self._pia._constants.background_enable_cmd,
            timeout_in_s,
            debug_option
        )
    
    def disable(
        self,
        timeout_in_s: None | int = None, 
        debug_option: bool = False
    ) -> str:
        """
        Stops the PIA daemon from running if the GUI 
        client is closed or has not been started.
        Disconnects the VPN and deactives the killswitch
        if the GUI client is not running.

        Returns the output of the command.
        """
        return self._pia._exec_one_shot_cmd(
            self._pia._constants.background_disable_cmd,
            timeout_in_s,
            debug_option
        )
