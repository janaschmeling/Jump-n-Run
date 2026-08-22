"""
Player character - movement, animation, physics.
"""
import os
import math
from ursina import Entity, Vec3, color, lerp, destroy
from game_config import LANE_X, GRAVITY, JUMP_SPEED


class JaguarPlayer:
    """The playable character: a jaguar with lane switching, jumping, crouching."""
    
    def __init__(self, model_path, scale=1.0):
        self.lane = 1  # center lane
        self.target_lane = 1
        self.x = LANE_X[self.lane]
        self.y = 0.0
        self.z = 0.0
        self.vert_velocity = 0.0
        self.grounded = True
        self.score = 0
        self.alive = True
        self.crouching = False

        # Create root entity for position/rotation
        self.root = Entity(model=None, position=Vec3(self.x, self.y, self.z))
        
        # Load visual model
        try:
            self.visual = Entity(parent=self.root, model=model_path, scale=scale, position=Vec3(0, 0, 0))
        except Exception:
            # Fallback to cube if model fails to load
            self.visual = Entity(parent=self.root, model='cube', scale=Vec3(1, 1, 1), color=color.azure)

        # Detect crouch animation
        self._detect_crouch_animation()
        
        # Prepare crouch scales for smooth transitions
        self._init_crouch_scales(scale)

    def _detect_crouch_animation(self):
        """Check if loaded model exposes crouch/duck animation clip."""
        self.has_crouch_anim = False
        self.crouch_anim_name = None
        try:
            anims = getattr(self.visual, 'animations', None)
            if anims:
                names = list(anims) if isinstance(anims, dict) else list(anims)
                for n in names:
                    if any(x in n.lower() for x in ['crouch', 'duck', 'sit']):
                        self.has_crouch_anim = True
                        self.crouch_anim_name = n
                        break
        except Exception:
            pass

    def _init_crouch_scales(self, scale):
        """Initialize base and crouch scales for smooth transitions."""
        s = self.visual.scale
        if isinstance(s, (int, float)):
            self.base_scale = Vec3(s, s, s)
        else:
            self.base_scale = Vec3(s.x, s.y, s.z)
        self.crouch_scale = Vec3(
            self.base_scale.x,
            max(0.35, self.base_scale.y * 0.55),
            self.base_scale.z
        )
        self.crouch_offset_y = -0.18 * scale

    def move_left(self):
        """Switch to the left lane (if not already at left edge)."""
        if self.target_lane > 0:
            self.target_lane -= 1

    def move_right(self):
        """Switch to the right lane (if not already at right edge)."""
        if self.target_lane < len(LANE_X) - 1:
            self.target_lane += 1

    def jump(self):
        """Jump if grounded."""
        if self.grounded:
            self.vert_velocity = JUMP_SPEED
            self.grounded = False

    def set_crouch(self, enable: bool):
        """Enable/disable crouch and play animation if available."""
        if enable and not self.crouching:
            if self.has_crouch_anim:
                play = getattr(self.visual, 'play', None)
                if callable(play):
                    try:
                        play(self.crouch_anim_name)
                    except Exception:
                        pass
        elif not enable and self.crouching:
            if self.has_crouch_anim:
                stop = getattr(self.visual, 'stop', None)
                if callable(stop):
                    try:
                        stop()
                    except Exception:
                        pass
        self.crouching = bool(enable)

    def update(self, dt):
        """Update player: lane interpolation, vertical physics, visuals."""
        # Smooth lane transition
        target_x = LANE_X[self.target_lane]
        self.x = lerp(self.x, target_x, 12 * dt)

        # Vertical physics (jump & fall)
        if not self.grounded:
            self.vert_velocity -= GRAVITY * dt
            self.y += self.vert_velocity * dt
            if self.y <= 0:
                self.y = 0
                self.vert_velocity = 0
                self.grounded = True

        # Update root position
        self.root.position = Vec3(self.x, self.y, self.z)

        # Smooth visual scale for crouch/stand
        target_scale = self.crouch_scale if self.crouching else self.base_scale
        vs = self.visual.scale
        if isinstance(vs, (int, float)):
            vs_vec = Vec3(vs, vs, vs)
        else:
            vs_vec = Vec3(vs.x, vs.y, vs.z)
        new_scale = lerp(vs_vec, target_scale, 8 * dt)
        self.visual.scale = new_scale

        # Adjust visual height for crouch
        current_y = getattr(self.visual, 'y', 0)
        target_y = self.crouch_offset_y if self.crouching else 0
        try:
            self.visual.y = lerp(current_y, target_y, 8 * dt)
        except Exception:
            pass

        # Smooth rotation
        self.root.rotation_y = lerp(self.root.rotation_y, 0, 6 * dt)

    def cleanup(self):
        """Destroy visual entities."""
        try:
            destroy(self.root)
        except Exception:
            pass
