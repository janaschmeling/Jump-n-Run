"""
World generation and management - segments, obstacles, coins.
"""
import random
from ursina import Entity, color, Vec3, destroy
from game_config import (SEGMENT_LENGTH, SEGMENT_WIDTH, OBSTACLE_CHANCE, 
                         COIN_CHANCE, OBSTACLE_SIZE, COIN_SIZE, LANE_X)


class Segment:
    """A ground segment (one chunk of the endless runner world)."""
    
    def __init__(self, z_pos):
        self.z = z_pos
        self.entity = Entity(
            model='cube',
            scale=(SEGMENT_WIDTH, 0.2, SEGMENT_LENGTH),
            color=color.rgb(40, 40, 50),
            position=(0, -0.1, self.z)
        )
        self.obstacles = []
        self.coins = []
        self.populate()

    def populate(self):
        """Randomly place obstacles and coins in this segment."""
        for lane_index, x in enumerate(LANE_X):
            if random.random() < OBSTACLE_CHANCE:
                z_off = random.uniform(
                    self.z - SEGMENT_LENGTH/2 + 2,
                    self.z + SEGMENT_LENGTH/2 - 2
                )
                obs = Entity(
                    model='cube',
                    scale=OBSTACLE_SIZE,
                    color=color.rgb(150, 40, 40),
                    position=(x, OBSTACLE_SIZE[1]/2, z_off)
                )
                self.obstacles.append(obs)
            elif random.random() < COIN_CHANCE:
                z_off = random.uniform(
                    self.z - SEGMENT_LENGTH/2 + 2,
                    self.z + SEGMENT_LENGTH/2 - 2
                )
                coin = Entity(
                    model='sphere',
                    scale=COIN_SIZE,
                    color=color.yellow,
                    position=(x, 0.4, z_off)
                )
                self.coins.append(coin)

    def update(self, dt, speed):
        """Move segment and all contained objects."""
        self.z -= speed * dt
        self.entity.z = self.z
        for o in self.obstacles:
            o.z -= speed * dt
        for c in self.coins:
            c.z -= speed * dt

    def destroy(self):
        """Clean up all entities in this segment."""
        try:
            destroy(self.entity)
        except Exception:
            pass
        for o in self.obstacles:
            try:
                destroy(o)
            except Exception:
                pass
        for c in self.coins:
            try:
                destroy(c)
            except Exception:
                pass


class WorldManager:
    """Manages the endless world: segment lifecycle, despawn/spawn."""
    
    def __init__(self):
        self.segments = []
        self.spawn_initial_segments()

    def spawn_initial_segments(self):
        """Create the initial set of segments."""
        for i in range(NUM_INITIAL_SEGMENTS := 10):  # walrus to avoid import
            seg = Segment(i * SEGMENT_LENGTH)
            self.segments.append(seg)

    def update(self, dt, speed):
        """Update all segments and recycle old ones."""
        for seg in self.segments:
            seg.update(dt, speed)

        # Despawn segments that have passed behind the player
        if self.segments and self.segments[0].z < -SEGMENT_LENGTH:
            old = self.segments.pop(0)
            old.destroy()
            # Spawn new segment at the far end
            new_seg = Segment(self.segments[-1].z + SEGMENT_LENGTH)
            self.segments.append(new_seg)

    def get_all_obstacles(self):
        """Return all active obstacles (for collision detection)."""
        obstacles = []
        for seg in self.segments:
            obstacles.extend(seg.obstacles)
        return obstacles

    def get_all_coins(self):
        """Return all active coins (for collection)."""
        coins = []
        for seg in self.segments:
            coins.extend(seg.coins)
        return coins

    def cleanup(self):
        """Destroy all segments (on shutdown)."""
        for seg in self.segments:
            seg.destroy()
        self.segments.clear()