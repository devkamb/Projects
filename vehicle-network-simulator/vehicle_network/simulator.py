from __future__ import annotations

import argparse
import json
import socket
import threading
from datetime import datetime
from pathlib import Path
from time import monotonic, sleep, time
from typing import Any

from vehicle_network.can_frame import CANFrame, FrameError


class VehicleNetworkSimulator:
    def __init__(self, log_path: Path, host: str = "127.0.0.1") -> None:
        self.host = host
        self.log_path = log_path
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._stats = {"valid_frames": 0, "invalid_frames": 0}

        self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_sock.bind((self.host, 0))
        self._udp_sock.settimeout(0.2)
        self.udp_port = self._udp_sock.getsockname()[1]

        self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._tcp_sock.bind((self.host, 0))
        self._tcp_sock.listen()
        self._tcp_sock.settimeout(0.2)
        self.tcp_port = self._tcp_sock.getsockname()[1]

        self._threads = [
            threading.Thread(target=self._udp_receiver, name="udp-receiver", daemon=True),
            threading.Thread(target=self._tcp_diagnostics, name="tcp-diagnostics", daemon=True),
        ]

    def start(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if self.log_path.exists():
            self.log_path.unlink()
        for thread in self._threads:
            thread.start()

    def stop(self) -> None:
        self._stop.set()
        for thread in self._threads:
            thread.join(timeout=1.0)
        self._udp_sock.close()
        self._tcp_sock.close()

    def send_frame(self, frame: CANFrame, corrupt: bool = False) -> None:
        payload = bytearray(frame.encode())
        if corrupt:
            payload[-2] = payload[-2] ^ 0x01
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            sender.sendto(bytes(payload), (self.host, self.udp_port))

    def status(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._stats)

    def _udp_receiver(self) -> None:
        while not self._stop.is_set():
            try:
                data, address = self._udp_sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break

            try:
                frame = CANFrame.decode(data)
            except FrameError as exc:
                with self._lock:
                    self._stats["invalid_frames"] += 1
                self._write_log(
                    {
                        "event": "frame_received",
                        "valid": False,
                        "error": str(exc),
                        "source": f"{address[0]}:{address[1]}",
                    }
                )
                continue

            with self._lock:
                self._stats["valid_frames"] += 1
            self._write_log(
                {
                    "event": "frame_received",
                    "valid": True,
                    "arbitration_id": frame.arbitration_id,
                    "dlc": frame.dlc,
                    "payload_hex": frame.payload.hex(),
                    "frame_timestamp": frame.timestamp,
                    "source": f"{address[0]}:{address[1]}",
                }
            )

    def _tcp_diagnostics(self) -> None:
        while not self._stop.is_set():
            try:
                client, _ = self._tcp_sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            with client:
                request = client.recv(1024).decode("utf-8").strip()
                if request:
                    try:
                        command = json.loads(request).get("command")
                    except json.JSONDecodeError:
                        command = "invalid"
                else:
                    command = "empty"

                response = {"ok": command == "status", "command": command, "status": self.status()}
                client.sendall((json.dumps(response, sort_keys=True) + "\n").encode("utf-8"))

    def _write_log(self, record: dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "monotonic": monotonic(),
            **record,
        }
        with self._lock:
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")


def query_status(host: str, port: int) -> dict[str, Any]:
    with socket.create_connection((host, port), timeout=2.0) as sock:
        sock.sendall(b'{"command":"status"}\n')
        response = sock.recv(4096)
    return json.loads(response.decode("utf-8"))


def build_demo_frames(sequence: int) -> list[CANFrame]:
    speed_kph = min(35, 5 + sequence)
    steering_deg = (sequence % 9) - 4
    implement_height = 40 + (sequence % 20)
    return [
        CANFrame(0x101, speed_kph.to_bytes(2, "big")),
        CANFrame(0x102, int(steering_deg + 40).to_bytes(1, "big")),
        CANFrame(0x201, int(implement_height).to_bytes(1, "big")),
    ]


def run_demo(duration: float, interval: float, log_path: Path, inject_bad_frame: bool = False) -> dict[str, Any]:
    simulator = VehicleNetworkSimulator(log_path=log_path)
    simulator.start()
    start = time()
    sequence = 0

    try:
        while time() - start < duration:
            for frame in build_demo_frames(sequence):
                simulator.send_frame(frame)
            if inject_bad_frame and sequence == 2:
                simulator.send_frame(CANFrame(0x155, b"\x01\x02"), corrupt=True)
            sequence += 1
            sleep(interval)
        sleep(0.2)
        diagnostic = query_status(simulator.host, simulator.tcp_port)
    finally:
        simulator.stop()

    return {
        "log_path": str(log_path),
        "duration": duration,
        "interval": interval,
        "diagnostic": diagnostic,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local vehicle network simulation")
    parser.add_argument("--duration", type=float, default=2.0)
    parser.add_argument("--interval", type=float, default=0.1)
    parser.add_argument("--log", type=Path, default=Path("logs/network_demo.jsonl"))
    parser.add_argument("--inject-bad-frame", action="store_true")
    args = parser.parse_args()

    summary = run_demo(args.duration, args.interval, args.log, args.inject_bad_frame)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
