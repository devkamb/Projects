import json
import unittest

from vehicle_network.can_frame import CANFrame, FrameError


class CANFrameTests(unittest.TestCase):
    def test_encode_decode_round_trip(self):
        frame = CANFrame(0x123, b"\x01\x02\x03")

        decoded = CANFrame.decode(frame.encode())

        self.assertEqual(frame.arbitration_id, decoded.arbitration_id)
        self.assertEqual(frame.payload, decoded.payload)
        self.assertEqual(frame.dlc, decoded.dlc)

    def test_rejects_payload_longer_than_classic_can(self):
        with self.assertRaises(FrameError):
            CANFrame(0x100, b"123456789")

    def test_rejects_invalid_arbitration_id(self):
        with self.assertRaises(FrameError):
            CANFrame(0x800, b"\x00")

    def test_rejects_checksum_mismatch(self):
        frame_dict = CANFrame(0x100, b"\x01").to_dict()
        frame_dict["checksum"] = (frame_dict["checksum"] + 1) % 256

        with self.assertRaises(FrameError):
            CANFrame.decode(json.dumps(frame_dict).encode("utf-8"))

    def test_rejects_dlc_payload_mismatch(self):
        frame_dict = CANFrame(0x100, b"\x01").to_dict()
        frame_dict["dlc"] = 8

        with self.assertRaises(FrameError):
            CANFrame.decode(json.dumps(frame_dict).encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
