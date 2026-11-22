import os
import time
from typing import Any, Dict
import yaml

try:
    import serial
except ImportError:
    serial = None


DEFAULT_CONFIG = {
    "experiment": {"name": "FCABP", "version": "1.1.0", "bids_root": "data", "initial_ambiguity": 0.45, "n_cues": 10},
    "hardware": {"trigger_mode": "keyboard", "scanner_sync_key": "5", "serial_port": "COM3", "baud_rate": 115200, "pulse_duration_ms": 10},
    "response_pad": {"belief": "1", "disbelief": "2", "suspend": "3", "quit_key": "q"},
    "ttl_codes": {"FIXATION_ONSET": 10, "PROPOSITION_ONSET": 20, "RESP_BELIEF": 31, "RESP_DISBELIEF": 32, "RESP_SUSPEND": 33, "FEEDBACK_ONSET": 40},
}


class HardwareInterface:
    """Abstracts MRI/EEG TTL triggers and response-pad mappings."""

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.cfg: Dict[str, Any] = yaml.safe_load(f)
        else:
            self.cfg = DEFAULT_CONFIG

        self.hw_cfg = self.cfg["hardware"]
        self.ttl_codes = self.cfg["ttl_codes"]
        self.key_map = self.cfg["response_pad"]
        self.mode = self.hw_cfg["trigger_mode"].lower()
        self._port = None

        if self.mode == "serial":
            if serial is None:
                raise RuntimeError("pyserial is required when trigger_mode is 'serial'.")
            self._port = serial.Serial(
                port=self.hw_cfg["serial_port"],
                baudrate=int(self.hw_cfg["baud_rate"]),
                timeout=0.01,
            )

    def send_trigger(self, event_name: str) -> int:
        code = int(self.ttl_codes[event_name])
        if self.mode == "serial" and self._port is not None:
            self._port.write(bytes([code]))
            time.sleep(self.hw_cfg["pulse_duration_ms"] / 1000.0)
            self._port.write(bytes())
        return code

    def translate_response(self, raw_key: str) -> str:
        key = raw_key.strip().lower()
        if key == str(self.key_map["belief"]).lower():
            return "BELIEF"
        if key == str(self.key_map["disbelief"]).lower():
            return "DISBELIEF"
        if key == str(self.key_map["suspend"]).lower():
            return "SUSPEND"
        if key == str(self.key_map["quit_key"]).lower():
            return "QUIT"
        return "SUSPEND"

    def close(self) -> None:
        if self._port is not None and self._port.is_open:
            self._port.close()
          
