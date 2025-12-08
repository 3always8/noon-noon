import unittest
import math
from noon.engine import NoonEngine
from noon.model import NoonState

class TestNoonEngine(unittest.TestCase):
    """
    Tests the pure logic of the NoonEngine without any Pygame dependency.
    """

    def setUp(self):
        """Set up common objects for testing."""
        self.width = 800
        self.height = 600
        self.engine = NoonEngine(self.width, self.height)
        self.state = NoonState()

    def test_resolution_independence(self):
        """Verify that base_radius is correctly calculated based on the smaller dimension."""
        engine_a = NoonEngine(800, 400)
        self.assertAlmostEqual(engine_a.base_radius, 400 * engine_a.base_radius_ratio)

        engine_b = NoonEngine(100, 200)
        self.assertAlmostEqual(engine_b.base_radius, 100 * engine_b.base_radius_ratio)
        
        engine_c = NoonEngine(150, 150)
        self.assertAlmostEqual(engine_c.base_radius, 150 * engine_c.base_radius_ratio)

    def test_gaze_mapping_center(self):
        """Test get_eye_center with neutral gaze (0,0) should return the exact center."""
        # For the right eye
        cx, cy = self.engine.get_eye_center(is_right_eye=True, state=self.state)
        expected_cx = (self.width / 2) + (self.width * self.engine.base_spacing_ratio)
        self.assertAlmostEqual(cx, expected_cx)
        self.assertAlmostEqual(cy, self.height / 2)

        # For the left eye
        cx, cy = self.engine.get_eye_center(is_right_eye=False, state=self.state)
        expected_cx = (self.width / 2) - (self.width * self.engine.base_spacing_ratio)
        self.assertAlmostEqual(cx, expected_cx)
        self.assertAlmostEqual(cy, self.height / 2)

    def test_gaze_mapping_head_turn(self):
        """Test that eye moves within the allowed 'max_pan' range."""
        max_pan_x = self.width * 0.3
        
        # Full right gaze
        state_right = NoonState(gaze_x=1.0, gaze_y=0)
        cx, _ = self.engine.get_eye_center(is_right_eye=True, state=state_right)
        expected_base_cx = (self.width / 2) + (self.width * self.engine.base_spacing_ratio)
        self.assertAlmostEqual(cx, expected_base_cx + max_pan_x)

        # Full left gaze
        state_left = NoonState(gaze_x=-1.0, gaze_y=0)
        cx, _ = self.engine.get_eye_center(is_right_eye=True, state=state_left)
        self.assertAlmostEqual(cx, expected_base_cx - max_pan_x)

    def test_eye_geometry_and_eccentricity(self):
        """Ensure that eye_eccentricity correctly makes the eye wider."""
        state = NoonState(eye_eccentricity=2.0, eye_scale=1.0)
        w, h = self.engine.get_eye_dimensions(state)
        
        # Width should be double the height for an eccentricity of 2.0
        self.assertAlmostEqual(w, 2.0 * h)
        
        # Check the base calculation
        expected_h = self.engine.base_radius * 2 * state.eye_scale
        self.assertAlmostEqual(h, expected_h)
        expected_w = expected_h * state.eye_eccentricity
        self.assertAlmostEqual(w, expected_w)

    def test_constraint_logic_with_extreme_inputs(self):
        """Ensure calculations do not crash with extreme (but valid) float inputs."""
        # Extreme values that might cause issues in some math operations
        extreme_state = NoonState(
            gaze_x=10000.0,
            gaze_y=-50000.0,
            eye_scale=100.0,
            eye_eccentricity=100.0
        )
        
        try:
            # Verify get_eye_center does not fail
            cx, cy = self.engine.get_eye_center(is_right_eye=True, state=extreme_state)
            self.assertTrue(math.isfinite(cx))
            self.assertTrue(math.isfinite(cy))

            # Verify get_eye_dimensions does not fail
            w, h = self.engine.get_eye_dimensions(extreme_state)
            self.assertTrue(math.isfinite(w))
            self.assertTrue(math.isfinite(h))

        except Exception as e:
            self.fail(f"Engine calculations failed with extreme inputs: {e}")

if __name__ == '__main__':
    unittest.main()
