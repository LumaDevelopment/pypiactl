from src._types import PIAInformationType
from src._utils import parse

from abc import ABC, abstractmethod
import subprocess
import threading
from typing import TypeVar, Generic

T = TypeVar('T')

class PIAMonitorObserver(ABC, Generic[T]):
    @abstractmethod
    def update(self, value: T) -> None:
        pass

class PIAMonitors():
    def __init__(self, pia):
        self._pia = pia

        self._monitors: dict[PIAInformationType, subprocess.Popen[str]] = {}
        self._observers: dict[PIAInformationType, list[PIAMonitorObserver]] = {}

    def _start_monitor(self, info: PIAInformationType) -> None:
        cmd = [self._pia._config.executable_path] + \
              self._pia._constants.monitor_cmd + \
              [info.value]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        self._monitors[info] = process

        def monitor_loop():
            if (not process.stdout):
                raise Exception('Subprocess has no standard output stream!')
            
            for line in process.stdout:
                value = parse(line.strip(), info)
                for observer in self._observers.get(info, []):
                    observer.update(value)

        threading.Thread(target=monitor_loop, daemon=True).start()

    def attach(self, info: PIAInformationType, observer: PIAMonitorObserver):
        if (info is PIAInformationType.REGIONS):
            return None

        if (info not in self._observers):
            self._observers[info] = []
        
        if (info not in self._monitors):
            self._start_monitor(info)

        self._observers[info].append(observer)

        # TODO return initial value using get cmd
        return True
    
    def _stop_monitor(self, info: PIAInformationType):
        process = self._monitors[info]
        if process:
            process.terminate()
            process.wait()
            del self._monitors[info]

    def detatch(self, info: PIAInformationType, observer: PIAMonitorObserver):
        if (info not in self._observers):
            return
        
        try:
            self._observers[info].remove(observer)
        except ValueError:
            return # no big deal
        
        if (len(self._observers[info]) == 0):
            self._stop_monitor(info)
