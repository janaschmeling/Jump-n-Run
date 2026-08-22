"""
Main game controller - orchestrates all systems and game loop.
"""
import os
import sys
import argparse
import urllib.request
from ursina import Ursina, camera, window, Text, color, Vec3, lerp, destroy

from game_config import (MODEL_DIR, DEFAULT_MODEL_URL, DEFAULT_MODEL_FILENAME,
                         WORLD_SPEED, CROUCH_SPEED_FACTOR, WINDOW_WIDTH, WINDOW_HEIGHT,
                         WINDOW_TITLE, CAMERA_FOLLOW_SPEED, CAMERA_OFFSET, CAMERA_ROTATION,
                         CAMERA_LOOK_OFFSET, SCORE_TEXT_POS, SCORE_TEXT_SCALE, 
                         INFO_TEXT_POS, INFO_TEXT_SCALE, PARTICLE_COUNT, PARTICLE_SPEED, LEAF_CHANCE)
from game_world import WorldManager
from game_player import JaguarPlayer
from game_particles import ParticleSystem
from game_input import InputManager
from game_collision import CollisionManager
import random


class GameApp:
    """Main game application - manages game loop and all subsystems."""
    
    def __init__(self, detector_cmd=None, pipe_mode=False, model_url=None, model_file=None):
        self.model_path = self._resolve_model_path(model_url, model_file)
        
        # Initialize Ursina
        self.app = Ursina()
        window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        window.title = WINDOW_TITLE
        camera.rotation = CAMERA_ROTATION
        camera.position = CAMERA_OFFSET

        # Load optional leaf texture
        leaf_tex = self._load_leaf_texture()

        # Initialize game systems
        self.input_manager = InputManager(detector_cmd, pipe_mode)
        self.world_manager = WorldManager()
        self.player = JaguarPlayer(self.model_path, scale=1.0)
        self.particle_system = ParticleSystem(leaf_tex)
        self.collision_manager = CollisionManager()

        # HUD
        self.score_text = Text(text='Score: 0', position=SCORE_TEXT_POS, scale=SCORE_TEXT_SCALE, color=color.white)
        self.info_text = Text(text='Move left/right, jump up, crouch down', position=INFO_TEXT_POS, scale=INFO_TEXT_SCALE, color=color.light_gray)

        # Game state
        self.game_over = False

        # Bind update and input
        self.app.update = self.update
        self.app.input = self.input

    def _resolve_model_path(self, model_url, model_file):
        """Determine which model to load."""
        if model_file:
            if not os.path.exists(model_file):
                print("Model file not found:", model_file, file=sys.stderr)
                sys.exit(1)
            return model_file
        
        model_path = os.path.join(MODEL_DIR, DEFAULT_MODEL_FILENAME)
        url = model_url or DEFAULT_MODEL_URL
        if not os.path.exists(model_path):
            self._download_model(url, model_path)
        return model_path

    def _download_model(self, url, out_path):
        """Download model if not present."""
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        print(f"Downloading model from {url} ...", file=sys.stderr)
        try:
            urllib.request.urlretrieve(url, out_path)
            print("Model downloaded.", file=sys.stderr)
        except Exception as e:
            print("Failed to download model:", e, file=sys.stderr)
            sys.exit(1)

    def _load_leaf_texture(self):
        """Optionally load leaf texture for particles."""
        try:
            from ursina import load_texture
            return load_texture('assets/leaf.png')
        except Exception:
            return None

    def update(self):
        """Main game loop - called every frame by Ursina."""
        if self.game_over:
            return

        dt = min(self.app.time_dt(), 1/30)  # Cap dt at 33ms

        # Poll detector input
        d, m = self.input_manager.get_input()

        # Handle one-shot direction input
        if d == 'left':
            self.player.move_left()
            self.input_manager.reset_direction()
        elif d == 'right':
            self.player.move_right()
            self.input_manager.reset_direction()

        # Handle one-shot movement input (up = jump)
        if m == 'up':
            self.player.jump()
            self.input_manager.reset_movement()

        # Handle continuous movement input (down = crouch)
        if m == 'down':
            self.player.set_crouch(True)
        else:
            self.player.set_crouch(False)

        # Update player
        self.player.update(dt)

        # Adjust world speed based on crouch
        current_speed = WORLD_SPEED * (CROUCH_SPEED_FACTOR if self.player.crouching else 1.0)

        # Update world
        self.world_manager.update(dt, current_speed)

        # Collision detection
        self._check_collisions()

        # Spawn particles at paws if moving between lanes
        self._spawn_movement_particles()

        # Update particles
        self.particle_system.update(dt)

        # Update HUD
        self.score_text.text = f'Score: {self.player.score}'

        # Update camera
        self._update_camera()

    def _check_collisions(self):
        """Check for obstacle collisions and coin collection."""
        # Obstacle collision
        obstacles = self.world_manager.get_all_obstacles()
        if self.collision_manager.check_obstacle_collision(self.player, obstacles):
            self._end_game()
            return

        # Coin collection
        coins = self.world_manager.get_all_coins()
        collected = self.collision_manager.collect_coins(self.player, coins)
        for c in collected:
            self.player.score += 1
            try:
                destroy(c)
            except Exception:
                pass
            # Remove from world manager's coin list
            for seg in self.world_manager.segments:
                if c in seg.coins:
                    seg.coins.remove(c)

    def _spawn_movement_particles(self):
        """Spawn particles when player changes lanes."""
        from game_config import LANE_X
        if abs(self.player.x - LANE_X[self.player.lane]) > 0.02:
            paw_positions = self.particle_system.get_paw_positions(self.player.root)
            spawn_pos = random.choice(paw_positions)
            self.particle_system.spawn_paw_particles(spawn_pos, PARTICLE_COUNT, PARTICLE_SPEED, LEAF_CHANCE)

    def _update_camera(self):
        """Update camera to follow player."""
        desired_cam = Vec3(self.player.x, CAMERA_OFFSET[1], self.player.z + CAMERA_OFFSET[2])
        camera.position = lerp(camera.position, desired_cam, CAMERA_FOLLOW_SPEED * self.app.time_dt())
        camera.look_at(self.player.root.position + Vec3(*CAMERA_LOOK_OFFSET))

    def _end_game(self):
        """Handle game over."""
        self.game_over = True
        print(f"Game Over! Final Score: {self.player.score}")
        self.info_text.text = f'Game Over - Score: {self.player.score}'
        self.app.pause()

    def input(self, key):
        """Handle keyboard input (fallback)."""
        if key in ('a', 'left arrow'):
            self.player.move_left()
        elif key in ('d', 'right arrow'):
            self.player.move_right()
        elif key == 'space':
            self.player.jump()
        elif key in ('s', 'down arrow'):
            self.player.set_crouch(True)

    def run(self):
        """Start the game."""
        try:
            self.app.run()
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up all systems on shutdown."""
        self.input_manager.shutdown()
        self.world_manager.cleanup()
        self.particle_system.cleanup()
        self.player.cleanup()


def main():
    parser = argparse.ArgumentParser(description='Jump N Run Game - 3 lanes with body movement control.')
    parser.add_argument('--run', dest='command', type=str, default=None, help='Command to run detector.')
    parser.add_argument('--pipe', action='store_true', help='Read detector JSON from stdin.')
    parser.add_argument('--model-url', type=str, default=None, help='GLB model URL.')
    parser.add_argument('--model-file', type=str, default=None, help='Local GLB file.')
    args = parser.parse_args()

    game = GameApp(
        detector_cmd=args.command,
        pipe_mode=args.pipe,
        model_url=args.model_url,
        model_file=args.model_file
    )
    game.run()


if __name__ == '__main__':
    main()
