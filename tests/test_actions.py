"""Unit tests for the action animation system.

Run from the skill folder:
    python -m unittest tests.test_actions -v

These tests verify the action calculations (timing, angles, offsets, end states),
not the visual quality of the rendered characters - inspect rendered frames for that.
"""
import unittest

from engine.actions import VALID_ACTIONS, normalize_action, sample_action


class ActionTests(unittest.TestCase):
    def test_action_not_started(self):
        action = normalize_action("collapse")
        result = sample_action(action, 1.0, 2.0, 1.0, 1.0)
        self.assertIsNone(result)

    def test_collapse_starts_upright(self):
        action = normalize_action("collapse")
        result = sample_action(action, 2.0, 2.0, 1.0, 1.0)
        self.assertAlmostEqual(result["whole_angle"], 0.0)

    def test_collapse_reaches_final_position(self):
        action = normalize_action({"name": "collapse", "duration": 0.9})
        result = sample_action(action, 2.0 + 0.9, 2.0, 1.0, 1.0)
        self.assertAlmostEqual(abs(result["whole_angle"]), 88.0, places=5)
        self.assertGreater(result["dy"], 20.0)             # the body settles onto the floor
        self.assertGreater(abs(result["dx"]), 40.0)        # the fallen body stays centred
        self.assertEqual(result["eyes"], "closed")         # unconscious end state
        self.assertEqual(result["pose"], "unconscious")
        self.assertEqual(result["bob"], 0.0)               # idle motion stopped

    def test_collapse_holds_after_it_finishes(self):
        action = normalize_action("collapse")
        finished = sample_action(action, 5.0, 2.0, 1.0, 1.0)
        much_later = sample_action(action, 30.0, 2.0, 1.0, 1.0)
        self.assertEqual(finished, much_later)             # stays down, never resumes idle

    def test_fall_direction_follows_facing(self):
        action = normalize_action({"name": "fall_forward"})
        facing_right = sample_action(action, 3.0, 2.0, 1.0, 1.0)
        facing_left = sample_action(action, 3.0, 2.0, 1.0, -1.0)
        self.assertGreater(facing_right["whole_angle"], 0.0)
        self.assertLess(facing_left["whole_angle"], 0.0)

    def test_fall_backward_opposes_facing(self):
        action = normalize_action({"name": "fall_backward"})
        result = sample_action(action, 3.0, 2.0, 1.0, 1.0)
        self.assertLess(result["whole_angle"], 0.0)

    def test_direction_overrides_the_facing_default(self):
        action = normalize_action({"name": "collapse", "direction": "left"})
        result = sample_action(action, 3.0, 2.0, 1.0, 1.0)
        self.assertLess(result["whole_angle"], 0.0)

    def test_slump_keeps_whole_body_upright(self):
        action = normalize_action({"name": "slump_forward", "duration": 1.0})
        result = sample_action(action, 3.0, 2.0, 1.0, 1.0)
        self.assertAlmostEqual(result["whole_angle"], 0.0)  # legs and pelvis stay put
        self.assertGreater(result["body_angle"], 40.0)      # upper body bends only
        self.assertGreater(result["head_angle"], 0.0)       # the head droops further
        self.assertAlmostEqual(result["dy"], 0.0)

    def test_get_up_reverses_a_collapse(self):
        action = normalize_action("get_up")
        on_the_ground = sample_action(action, 2.0, 2.0, 1.0, 1.0)
        self.assertAlmostEqual(abs(on_the_ground["whole_angle"]), 88.0, places=5)
        self.assertEqual(on_the_ground["eyes"], "closed")
        stood_up = sample_action(action, 2.0 + 0.9, 2.0, 1.0, 1.0)
        self.assertAlmostEqual(stood_up["whole_angle"], 0.0, places=5)
        self.assertEqual(stood_up["eyes"], "dot")
        self.assertEqual(stood_up["pose"], "idle")

    def test_state_scales_with_character_size(self):
        action = normalize_action("collapse")
        big = sample_action(action, 3.0, 2.0, 2.0, 1.0)
        small = sample_action(action, 3.0, 2.0, 0.5, 1.0)
        self.assertAlmostEqual(big["dy"], small["dy"] * 4.0, places=5)
        self.assertAlmostEqual(big["dx"], small["dx"] * 4.0, places=5)

    def test_no_action_returns_none(self):
        self.assertIsNone(normalize_action(None))
        self.assertIsNone(sample_action(None, 1.0, 0.0, 1.0, 1.0))

    def test_unknown_action_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_action("backflip")
        with self.assertRaises(ValueError):
            normalize_action({"name": "collapse", "direction": "sideways"})

    def test_all_valid_actions_sample(self):
        keys = ("dx", "dy", "pose", "emotion", "eyes", "mouth", "bob", "squash",
                "whole_angle", "body_angle", "head_angle")
        for name in sorted(VALID_ACTIONS):
            state = sample_action(normalize_action(name), 10.0, 0.0, 1.0, 1.0)
            self.assertIsNotNone(state, name)
            for key in keys:
                self.assertIn(key, state, f"{name} is missing {key}")

    def test_motion_is_smooth_at_both_ends(self):
        action = normalize_action("collapse")
        start = sample_action(action, 2.0, 2.0, 1.0, 1.0)
        early = sample_action(action, 2.02, 2.0, 1.0, 1.0)
        self.assertLess(abs(early["whole_angle"] - start["whole_angle"]), 1.0)


if __name__ == "__main__":
    unittest.main()
