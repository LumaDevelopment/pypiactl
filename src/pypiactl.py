# Internal Imports
from ._background import PIABackground
from ._config import PIAConfig
from ._constants import PIAConstants

# External Imports
import subprocess
import warnings

class PIA():
    def __init__(self, config: PIAConfig=PIAConfig()):
        self._config = config
        self._constants = PIAConstants()

        self.background = PIABackground(self)
        """
        Allow the killswitch and/or VPN connection to remain active
        in the background when the GUI client is not running. When 
        enabled, the PIA daemon will stay active even if the GUI 
        client is closed or has not been started. This allows 
        connection even if the GUI client is not running. Disabling 
        background activation will disconnect the VPN and deactivate 
        killswitch if the GUI client is not running.
        """

    def _exec_one_shot_cmd(
        self, 
        cmd: list[str], 
        timeout_in_s: None | int = None, 
        debug_option: bool = False
    ) -> str:
        # Assemble full command from executable, 
        # options, and provided command.
        full_cmd = [self._config.executable_path]

        # Timeout option
        timeout = None
        if timeout_in_s:
            if timeout_in_s < 1:
                warnings.warn("One-shot command timeout must be 1 or greater if not None! Ignoring!")
            else:
                timeout = timeout_in_s
        elif self._config.one_shot_timeout_in_s:
            timeout = self._config.one_shot_timeout_in_s

        if timeout:
            full_cmd += [self._constants.timeout_flag, str(timeout)]

        # Debug option
        debug = None
        if debug_option:
            debug = debug_option
        elif self._config.debug_option:
            debug = self._config.debug_option
        
        if debug:
            full_cmd += [self._constants.debug_flag]
        
        full_cmd += cmd

        # Execute it
        result = subprocess.run(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        return result.stdout.strip()
    
    def connect(
        self,
        timeout_in_s: None | int = None, 
        debug_option: bool = False
    ):
        """
        Connects to the VPN, or reconnects to apply new settings. 
        To use this command, the PIA GUI client must be running, 
        or background mode must be enabled.
        (By default, he PIA daemon is inactive when the GUI client
        is not running.)
        """
        return self._exec_one_shot_cmd(
            self._constants.connect_cmd,
            timeout_in_s,
            debug_option
        )
    