from ._types import PIAInformationType, PIAMonitorObserver
from ._utils import parse

import subprocess
import threading

class PIAMonitors():
    def __init__(self, pia):
        self._pia = pia

        self._monitors: dict[PIAInformationType, subprocess.Popen[str]] = {}
        self._observers: dict[PIAInformationType, list[PIAMonitorObserver]] = {}

    def _start_monitor(self, info_type: PIAInformationType):
        cmd = [self._pia._config.executable_path] + \
              self._pia._constants.monitor_cmd + \
              [info_type.value]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        self._monitors[info_type] = process

        def monitor_loop():
            if (not process.stdout):
                raise Exception('Subprocess has no standard output stream!')
            
            for line in process.stdout:
                value = parse(line.strip(), info_type)
                for observer in self._observers.get(info_type, []):
                    observer.update(value)

        threading.Thread(target=monitor_loop, daemon=True).start()

    def attach(self, info_type: PIAInformationType, observer: PIAMonitorObserver):
        """
        Register the given observer to receive updates whenever 
        the specified information changes.

        Map from `PIAInformationType` to the type of the value that 
        the observer will be updated with (see `PIA`'s `get` method
        for more information):
        - `ALLOW_LAN`, `DEBUG_LOGGING`, `REQUEST_PORT_FORWARD` ->
        `bool`
        - `CONNECTION_STATE` -> `PIAConnectionState`
        - `PORT_FORWARD` -> `int` or `PIAPortForwardStatus`
        - `PROTOCOL` -> `PIAProtocol`
        - `PUB_IP`, `VPN_IP` -> `ipaddress.IPv4Address` or `None`
        - `REGION` -> `str`

        Returns the current value for the given information type.
        Returns `None` if the given information type is `REGIONS`, 
        as `REGIONS` is not monitorable.
        """

        if (info_type is PIAInformationType.REGIONS):
            return None

        if (info_type not in self._observers):
            self._observers[info_type] = []
        
        if (info_type not in self._monitors):
            self._start_monitor(info_type)

        self._observers[info_type].append(observer)

        return self._pia.get(info_type).data
    
    def _stop_monitor(self, info_type: PIAInformationType):
        process = self._monitors[info_type]
        if process:
            process.terminate()
            process.wait()
            del self._monitors[info_type]

    def detatch(self, info_type: PIAInformationType, observer: PIAMonitorObserver):
        """
        Unregisters the given observer for the given information type, 
        meaning it will no longer be updated when the specified 
        information changes.
        """

        if (info_type not in self._observers):
            return
        
        try:
            self._observers[info_type].remove(observer)
        except ValueError:
            return # no big deal
        
        if (len(self._observers[info_type]) == 0):
            self._stop_monitor(info_type)
