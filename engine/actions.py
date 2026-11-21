"""ReachMora action animation system.
Converts named character actions into deterministic animation states.
All timing is expressed in seconds on the final output timeline."""
import math

VALID_ACTIONS = {
    "collapse",
    "fall_forward",
    "fall_backward",
    "slump_forward",
    "get_up",
}

DIRECTIONS = ("auto", "forward", "backward", "left", "right")

# Geometry mirrored from kit.py so this module stays import-light.
# BODY_BOT is the pelvis (-128): the pivot every whole-body rotation uses.
# FALL_CENTER (82) is where the centre of a fallen body sits relative to that pivot,
# so the character stays in frame instead of swinging to one side.
# FLOOR_DROP (44) lowers the body until its silhouette rests on the floor line.
BODY_BOT = -128.0
FALL_CENTER = 82.0
FLOOR_DROP = 44.0
FULL_ANGLE = 88.0     # degrees the whole body rotates when it goes down
SLUMP_ANGLE = 55.0    # degrees the upper body alone rotates in a slump
SLUMP_HEAD = 22.0     # extra head droop on top of the slump


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smoothstep(value):
    """Smooth transition with zero velocity at both endpoints."""
    p = clamp(value)
    return p * p * (3.0 - 2.0 * p)


def normalize_action(value):
    """Validate and normalize a story.json action specification.
    Accepts a bare name ("collapse") or an object; returns None for no action."""
    if value is None:
        return None
    if isinstance(value, str):
        value = {"name": value}
    if not isinstance(value, dict):
        raise ValueError(f"action must be a name or an object, got {type(value).__name__}")
    name = str(value.get("name", "")).strip().lower()
    if name not in VALID_ACTIONS:
        raise ValueError(f"unknown action '{name}'. Options: {', '.join(sorted(VALID_ACTIONS))}")
    direction = str(value.get("direction", "auto")).strip().lower()
    if direction not in DIRECTIONS:
        raise ValueError(f"unknown action direction '{direction}'. Options: {', '.join(DIRECTIONS)}")
    return {
        "name": name,
        "at": value.get("at"),
        "duration": max(0.1, float(value.get("duration", 0.9))),
        "direction": direction,
    }


def _sign(action, facing):
    """+1 = towards screen right. Falls follow the face unless the direction says otherwise."""
    direction = action.get("direction", "auto")
    if direction == "auto":
        direction = "backward" if action["name"] == "fall_backward" else "forward"
    if direction == "left":
        return -1.0
    if direction == "right":
        return 1.0
    face = 1.0 if facing >= 0 else -1.0
    return -face if direction == "backward" else face


def sample_action(action, t, start, scale=1.0, facing=0.0):
    """Sample an action at time t.

    Returns None before the action starts (and when there is no action), otherwise a
    state dict consumed by Actor.draw() / Crowd.world():
      dx, dy        offsets in output pixels (already multiplied by `scale`)
      pose          POSES key for the arms
      emotion       EMOTIONS key for brow / extras
      eyes, mouth   expression overrides
      bob, squash   replacements for the idle motion
      whole_angle   rotation of the whole character about the pelvis (degrees)
      body_angle    rotation of the upper body about the pelvis (degrees)
      head_angle    extra head rotation (degrees)
    Once the action has finished the dict keeps its final values, so an unconscious
    character stays down instead of resuming the idle animation."""
    if not action or start is None:
        return None
    if t < start:
        return None
    u = clamp((t - start) / max(0.05, float(action.get("duration", 0.9))))
    p = smoothstep(u)
    sign = _sign(action, facing)
    drop = FLOOR_DROP * scale * p          # settle the body onto the floor
    shift = -sign * FALL_CENTER * scale * p  # keep the fallen body centred on x
    name = action["name"]
    state = dict(dx=0.0, dy=0.0, pose="idle", emotion="neutral", eyes="dot", mouth="flat",
                 bob=0.0, squash=0.0, whole_angle=0.0, body_angle=0.0, head_angle=0.0)
    if name in ("collapse", "fall_forward", "fall_backward"):
        # Whole body rotates about the pelvis and settles onto the ground.
        state["whole_angle"] = sign * FULL_ANGLE * p
        state["dx"] = shift
        state["dy"] = drop
        state["head_angle"] = -sign * 8.0 * p          # the head lags the fall a little
        state["pose"] = "falling" if u < .85 else "unconscious"
        state["emotion"] = "shocked" if u < .7 else "neutral"
        state["eyes"] = "wide" if u < .55 else "closed"
        state["mouth"] = "o" if u < .75 else "flat"
        state["squash"] = .12 * math.sin(clamp((u - .7) / .3) * math.pi)
    elif name == "slump_forward":
        # Upper body only: the legs and pelvis keep standing or seated.
        state["body_angle"] = sign * SLUMP_ANGLE * p
        state["head_angle"] = sign * SLUMP_HEAD * p
        state["pose"] = "slumped"
        state["emotion"] = "shocked" if u < .5 else "neutral"
        state["eyes"] = "wide" if u < .5 else "closed"
        state["mouth"] = "o" if u < .5 else "flat"
        state["squash"] = .05 * math.sin(u * math.pi)
    elif name == "get_up":
        # The reverse of a fall: it starts in the fallen end state and rises.
        q = 1.0 - p
        state["whole_angle"] = sign * FULL_ANGLE * q
        state["dx"] = -sign * FALL_CENTER * scale * q
        state["dy"] = FLOOR_DROP * scale * q
        state["head_angle"] = -sign * 8.0 * q
        state["pose"] = "pushing_up" if u < .8 else "idle"
        state["emotion"] = "tired" if u < .7 else "neutral"
        state["eyes"] = "closed" if u < .45 else "dot"
        state["mouth"] = "flat" if u < .7 else "smile"
        state["squash"] = .08 * math.sin(clamp((u - .15) / .4) * math.pi)
    return state
