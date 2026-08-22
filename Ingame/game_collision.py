"""
Collision detection and game logic.
"""


class CollisionManager:
    """Handles collision detection and scoring."""
    
    @staticmethod
    def check_obstacle_collision(player, obstacles):
        """Check if player hit an obstacle. Returns True if collision."""
        for obs in obstacles:
            if obs is None or not obs.enabled:
                continue
            if (abs(obs.x - player.x) < 0.6 and
                abs(obs.z - player.z) < 0.9 and
                player.y < obs.y + 0.2):
                return True
        return False

    @staticmethod
    def collect_coins(player, coins):
        """Check for coin collisions and return newly collected coins."""
        collected = []
        for c in list(coins):
            if c is None or not c.enabled:
                continue
            if (abs(c.x - player.x) < 0.6 and
                abs(c.z - player.z) < 0.9 and
                player.y < 1.2):
                collected.append(c)
        return collected
