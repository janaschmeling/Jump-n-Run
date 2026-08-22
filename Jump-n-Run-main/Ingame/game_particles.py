"""
Particle system - dirt and leaf effects at paws.
"""
import math
import random
from ursina import Entity, Vec3, color, destroy


class Particle:
    """A single particle (dirt or leaf) with physics and fade-out."""
    
    def __init__(self, position, velocity, color_, lifetime, model='quad', texture=None):
        self.entity = Entity(
            model=model,
            position=position,
            scale=0.07,
            color=color_,
            double_sided=True
        )
        if texture:
            try:
                self.entity.texture = texture
            except Exception:
                pass
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt):
        """Update particle: apply gravity, fade, scale down."""
        self.age += dt
        if self.age >= self.lifetime:
            try:
                destroy(self.entity)
            except Exception:
                pass
            return False

        # Apply gravity (reduced)
        self.velocity.y -= 9.8 * dt * 0.6
        self.entity.position += self.velocity * dt

        # Fade out alpha
        alpha = max(0, 1.0 - (self.age / self.lifetime))
        c = self.entity.color
        self.entity.color = color.rgba(c.r, c.g, c.b, alpha)

        # Scale down
        self.entity.scale *= (1.0 - 0.6 * dt)
        return True


class ParticleSystem:
    """Manages spawning and updating particles."""
    
    def __init__(self, leaf_tex=None):
        self.particles = []
        self.leaf_tex = leaf_tex

    def spawn_paw_particles(self, world_pos, particle_count=8, particle_speed=3.5, leaf_chance=0.35):
        """Spawn particles at a world position (e.g., paw contact point)."""
        for i in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.3 * particle_speed, particle_speed)
            vx = math.cos(angle) * 0.5 * speed
            vz = math.sin(angle) * 0.5 * speed
            vy = random.uniform(1.0, 2.4)
            vel = Vec3(vx, vy, vz)

            is_leaf = random.random() < leaf_chance
            if is_leaf and self.leaf_tex:
                col = color.rgb(80, 160, 40)
                p = Particle(
                    world_pos + Vec3(random.uniform(-0.05, 0.05), 0, random.uniform(-0.05, 0.05)),
                    vel,
                    col,
                    0.9,
                    model='quad',
                    texture=self.leaf_tex
                )
            else:
                col = color.rgb(120, 80, 40)
                p = Particle(
                    world_pos + Vec3(random.uniform(-0.05, 0.05), 0, random.uniform(-0.05, 0.05)),
                    vel,
                    col,
                    0.9,
                    model='cube',
                    texture=None
                )
            self.particles.append(p)

    def update(self, dt):
        """Update all particles and remove dead ones."""
        new_particles = []
        for p in self.particles:
            keep = p.update(dt)
            if keep:
                new_particles.append(p)
        self.particles[:] = new_particles

    def cleanup(self):
        """Destroy all particles."""
        for p in self.particles:
            try:
                destroy(p.entity)
            except Exception:
                pass
        self.particles.clear()

    def get_paw_positions(self, player_root):
        """Calculate world positions of paws from player root."""
        # Approximate paw offsets in local space
        offsets = [
            Vec3(0.45, -0.45, 0.35),   # front-right
            Vec3(0.45, -0.45, -0.35),  # front-left
            Vec3(-0.45, -0.45, 0.35),  # back-right
            Vec3(-0.45, -0.45, -0.35)  # back-left
        ]
        poses = []
        angle = math.radians(player_root.rotation_y)
        for off in offsets:
            x = off.x * math.cos(angle) - off.z * math.sin(angle)
            z = off.x * math.sin(angle) + off.z * math.cos(angle)
            world = player_root.world_position + Vec3(x, off.y, z)
            poses.append(world)
        return poses
