# Vehicle Network Communication Simulator

This project simulates controller-to-controller communication using UDP for periodic CAN-style messages and TCP for diagnostic status queries.

## What It Demonstrates

- UDP socket communication
- TCP request-response diagnostics
- CAN-style frame structure
- Packet validation and checksum detection
- Message timing analysis
- Controller-network logging and debugging

## Run It

```bash
bash scripts/run_demo.sh
```

Run validation:

```bash
bash scripts/run_validation.sh
```

## Project Structure

```text
vehicle_network/
  can_frame.py       CAN-style frame encode/decode and checksum validation
  simulator.py       UDP receiver, sender, and TCP diagnostic server
  validator.py       Log validator for timing and packet-quality checks
tests/
  test_can_frame.py
scripts/
  run_demo.sh
  run_validation.sh
```

## How This Maps To RFA

The RFA posting lists UDP, TCP/IP, CAN, embedded systems, Linux, and debugging as desired attributes. This project shows those fundamentals in a local simulation that is easy to run and explain.
