import queue
import threading

import numpy as np
import sounddevice as sd


def list_input_devices() -> list[dict]:
    devices = []
    for index, device in enumerate(sd.query_devices()):
        if device.get("max_input_channels", 0) > 0:
            devices.append({"index": index, "name": device["name"]})
    return devices


class MicrophoneMonitor:
    """Small non-recording input meter. Audio is measured and discarded."""

    def __init__(self, device_index: int | None = None, samplerate: int = 16000):
        self.device_index = device_index
        self.samplerate = samplerate
        self._stream = None
        self._lock = threading.Lock()
        self._level = 0.0
        self._errors: queue.Queue[str] = queue.Queue()

    def _callback(self, indata, frames, time_info, status):
        if status:
            self._errors.put(str(status))
        if indata.size:
            rms = float(np.sqrt(np.mean(np.square(indata.astype(np.float32)))))
            with self._lock:
                self._level = min(1.0, rms * 5.0)

    def start(self):
        if self._stream is not None:
            return
        self._stream = sd.InputStream(
            device=self.device_index,
            channels=1,
            samplerate=self.samplerate,
            dtype="float32",
            blocksize=1024,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            self._level = 0.0

    def level(self) -> float:
        with self._lock:
            return self._level

    def pop_error(self) -> str | None:
        try:
            return self._errors.get_nowait()
        except queue.Empty:
            return None
