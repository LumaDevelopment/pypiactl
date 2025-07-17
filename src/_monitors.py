from ._types import PIAInformationType
from ._utils import parse

from abc import ABC, abstractmethod
import subprocess
import threading
from typing import TypeVar, Generic

T = TypeVar('T')

class PIAMonitorObserver(ABC, Generic[T]):
    @abstractmethod
    def update(self, value: T) -> None:
        pass

# TODO add comments to methods

class PIAMonitors():
    def __init__(self, pia):
        self._pia = pia

        self._monitors: dict[PIAInformationType, subprocess.Popen[str]] = {}
        self._observers: dict[PIAInformationType, list[PIAMonitorObserver]] = {}

    def _start_monitor(self, info_type: PIAInformationType) -> None:
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
        if (info_type not in self._observers):
            return
        
        try:
            self._observers[info_type].remove(observer)
        except ValueError:
            return # no big deal
        
        if (len(self._observers[info_type]) == 0):
            self._stop_monitor(info_type)
