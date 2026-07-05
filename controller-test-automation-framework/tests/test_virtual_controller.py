import unittest

from controller_framework.virtual_controller import ControllerMode, SensorFrame, VirtualImplementController


class VirtualImplementControllerTests(unittest.TestCase):
    def test_boot_transitions_to_idle(self):
        controller = VirtualImplementController()

        result = controller.apply_command("boot")

        self.assertTrue(result.accepted)
        self.assertEqual(ControllerMode.IDLE, result.mode)
        self.assertEqual("boot_complete", result.reason)

    def test_start_auto_requires_boot(self):
        controller = VirtualImplementController()
        sensors = SensorFrame(1200, 2400, 0, 50)

        result = controller.apply_command("start_auto", sensors)

        self.assertFalse(result.accepted)
        self.assertEqual(ControllerMode.OFF, result.mode)
        self.assertEqual("controller_not_booted", result.reason)

    def test_emergency_stop_latches_fault(self):
        controller = VirtualImplementController()
        controller.apply_command("boot")

        result = controller.apply_command("start_auto", SensorFrame(1200, 2400, 0, 50, e_stop=True))
        retry = controller.apply_command("start_auto", SensorFrame(1200, 2400, 0, 50, e_stop=False))

        self.assertFalse(result.accepted)
        self.assertEqual(ControllerMode.FAULT, result.mode)
        self.assertIn("emergency_stop_active", result.faults)
        self.assertFalse(retry.accepted)
        self.assertEqual("fault_latched", retry.reason)

    def test_clear_faults_returns_to_idle(self):
        controller = VirtualImplementController()
        controller.apply_command("boot")
        controller.apply_command("start_auto", SensorFrame(1200, 3301, 0, 50))

        result = controller.apply_command("clear_faults")

        self.assertTrue(result.accepted)
        self.assertEqual(ControllerMode.IDLE, result.mode)
        self.assertEqual((), result.faults)

    def test_raise_command_requires_active_mode(self):
        controller = VirtualImplementController()
        controller.apply_command("boot")

        result = controller.apply_command("raise", SensorFrame(1200, 2400, 0, 50))

        self.assertFalse(result.accepted)
        self.assertEqual("auto_not_active", result.reason)


if __name__ == "__main__":
    unittest.main()
