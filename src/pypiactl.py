# Internal Imports
from ._background import PIABackground
from ._config import PIAConfig
from ._constants import PIAConstants
from ._dedicated_ip import PIADedicatedIP
from ._monitors import PIAMonitors
from ._types import PIACommandResult, PIACommandStatus, PIAInformationType
from ._utils import parse

# External Imports
import subprocess
import warnings

# CLI SRC: https://github.com/pia-foss/desktop/tree/master/cli/src
# TODO add login command
# TODO add logout command
# TODO add set command
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

        self.dedicated_ip = PIADedicatedIP(self)
        """
        Add or remove a Dedicated IP.
        """

        self.monitor = PIAMonitors(self)
        """
        Monitors the PIA daemon for changes in a specific setting or 
        state value.\n
        When an observer attaches, the current value is returned.\n
        When a change is received, the observer is updated.
        """

    def _get_cmd_timeout(
        self,
        parameter_timeout: None | int
    ) -> None | int:
        """
        Determines if there will be a timeout flag for a
        command, and if there is, what the value will be.
        """
        if parameter_timeout:
            if parameter_timeout < 1:
                warnings.warn("One-shot command timeout must be 1 or greater if not None! Ignoring!")
                return None
            else:
                return parameter_timeout
        elif self._config.one_shot_timeout_in_s:
            return self._config.one_shot_timeout_in_s
        else:
            return None
        
    def _get_cmd_debug(
        self,
        parameter_debug: bool
    ) -> bool:
        """
        Determines whether a command will include its 
        debug logs in its returned output.
        """
        if parameter_debug:
            return parameter_debug
        elif self._config.debug_option:
            return self._config.debug_option
        else:
            return False

    def _exec_one_shot_cmd(
        self, 
        cmd: list[str], 
        timeout_in_s: None | int = None, 
        debug_option: bool = False
    ) -> tuple[int, str]:
        # Assemble full command from executable, 
        # options, and provided command.
        full_cmd = [self._config.executable_path]

        # Timeout option
        timeout = self._get_cmd_timeout(timeout_in_s)
        if timeout:
            full_cmd += [self._constants.timeout_flag, str(timeout)]

        # Debug option
        debug = self._get_cmd_debug(debug_option)
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
        
        return (result.returncode, result.stdout.strip())
    
    def connect(self, **kwargs) -> PIACommandResult[PIACommandStatus, None]:
        """
        Connects to the VPN, or reconnects to apply new settings. 
        To use this command, the PIA GUI client must be running, 
        or background mode must be enabled.
        (By default, the PIA daemon is inactive when the GUI client
        is not running.)
        """
        code, logs = self._exec_one_shot_cmd(
            self._constants.connect_cmd,
            **kwargs
        )

        return PIACommandResult[PIACommandStatus, None](
            PIACommandStatus.from_cli_exit_code(code),
            None, logs
        )
    
    def disconnect(self, **kwargs) -> PIACommandResult[PIACommandStatus, None]:
        """
        Disconnects from the VPN.
        """
        code, logs = self._exec_one_shot_cmd(
            self._constants.disconnect_cmd,
            **kwargs
        )

        return PIACommandResult[PIACommandStatus, None](
            PIACommandStatus.from_cli_exit_code(code),
            None, logs
        )
    
    def get(self, info_type: PIAInformationType, **kwargs):
        """
        Get information from the PIA daemon.\n
        Available types:\n
        - `ALLOW_LAN` - Whether to allow LAN traffic (returns `bool`)
        - `CONNECTION_STATE` - VPN connection state (returns `PIAConnectionState`)
        - `DEBUG_LOGGING` - State of debug logging setting (returns `bool`)
        - `PORT_FORWARD` - Forwarded port number if available, or the status of 
          the request to forward a port (returns `int` or `PIAPortForwardStatus`)
        - `PROTOCOL` - VPN connection protocol (returns `PIAProtocol`)
        - `PUB_IP` - Current public IP address (returns `IPv4Address` or `None`)
        - `REGION` - Currently selected region (or "auto") (returns `str`)
        - `REGIONS` - List all available regions (returns `set[str]`)
        - `REQUEST_PORT_FORWARD` - Whether a forwarded port will be requested on
          the next connection attempt (returns `bool`)
        - `VPN_IP` - Current VPN IP address (returns `IPv4Address` or `None`)
        """
        code, logs = self._exec_one_shot_cmd(
            self._constants.get_cmd + [info_type.value],
            **kwargs
        )

        value = parse(
            logs.splitlines()[-1].strip(),
            info_type
        )

        return PIACommandResult[PIACommandStatus, type(value)](
            PIACommandStatus.from_cli_exit_code(code),
            value, logs
        )
    
    def reset_settings(self, **kwargs) -> PIACommandResult[PIACommandStatus, None]:
        """
        Resets daemon settings to the defaults (ports/protocols/etc.)
        Client settings (themes/icons/layouts) can't be set with the CLI.
        """
        code, logs = self._exec_one_shot_cmd(
            self._constants.reset_settings_cmd,
            **kwargs
        )

        return PIACommandResult[PIACommandStatus, None](
            PIACommandStatus.from_cli_exit_code(code),
            None, logs
        )

    def version(self) -> str:
        """
        Returns version information.
        """

        return self._exec_one_shot_cmd(
            self._constants.version_cmd
        )[1]
