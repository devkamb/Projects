# Learning Guide: Vehicle Network Communication Simulator

## Core Idea

Vehicle and off-road equipment controllers exchange short messages. Real systems often use CAN, but this project uses local UDP and TCP sockets so you can practice the ideas without hardware.

UDP is used for periodic control messages because it is lightweight. TCP is used for diagnostics because it is reliable and connection-oriented.

## Files To Study In Order

1. `vehicle_network/can_frame.py`
   - Learn arbitration IDs, payload length, encoding, decoding, and checksum validation.
2. `vehicle_network/simulator.py`
   - Learn how UDP receivers, UDP senders, and TCP diagnostic requests work.
3. `vehicle_network/validator.py`
   - Learn how logs can be checked for invalid packets, missing messages, and timing gaps.
4. `tests/test_can_frame.py`
   - Learn the unit tests for frame validation.

## CAN-Style Concepts

Arbitration ID:

The message identifier. In real CAN, lower IDs have higher priority during bus arbitration.

DLC:

Data length code. Classic CAN payloads are usually 0 to 8 bytes.

Payload:

The raw data bytes carried by the message.

Checksum:

A small validation value that helps detect corrupted messages. Real protocols may use CRCs or frame-level error detection.

## Interview Explanation

I built a Python network simulator that sends CAN-style frames over UDP and exposes diagnostic status over TCP. The frame includes an arbitration ID, data length, payload, timestamp, and checksum. The simulator logs valid and invalid packets, and the validator checks packet quality and timing gaps. This helped me practice network fundamentals relevant to controller communication.

## Practice Changes

1. Add a new frame ID for GPS position.
2. Add a validator rule that requires each arbitration ID to appear at least once.
3. Add a packet-loss option to the simulator.
4. Replace the simple checksum with CRC-8.
