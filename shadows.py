import math
import random
import time
import pygame
from math import atan2, cos, sin, floor
from typing import List, Tuple

class FOVSystem:
    def __init__(self, blocks: List[pygame.Rect], 
                 fov_angle: float = 90, 
                 base_ray_count: int = 60,
                 view_distance: int = 200,
                 ray_density: float = 0.5,
                 grid_size: int = 64):
        """
        Initialize the Field of View system with ray casting.
        
        Args:
            blocks: List of all blocking rectangles in the level
            fov_angle: Field of view angle in degrees
            base_ray_count: Minimum number of rays to cast
            view_distance: Maximum view distance in pixels
            ray_density: Rays per pixel at max distance
            grid_size: Size of spatial partitioning grid cells
        """
        self.blocks = blocks
        self.fov_angle = fov_angle
        self.base_ray_count = base_ray_count
        self.view_distance = view_distance
        self.ray_density = ray_density
        self.grid_size = grid_size
        
        # Initialize spatial partitioning
        self.grid = {}
        self._init_spatial_partition()
        
        # Create darkness surface
        self.lightness_frames = 0
        self.darkness_frames = 0
        self.dark = False
        self.light_on = True
    def _init_spatial_partition(self):
        """Optimized spatial partitioning initialization"""
        self.grid = {}
        for block in self.blocks:
            # Calculate all grid cells this block touches
            min_gx = floor(block.left / self.grid_size)
            max_gx = floor(block.right / self.grid_size)
            min_gy = floor(block.top / self.grid_size)
            max_gy = floor(block.bottom / self.grid_size)
            
            # Add to all relevant grid cells
            for gx in range(min_gx, max_gx + 1):
                for gy in range(min_gy, max_gy + 1):
                    key = (gx, gy)
                    if key not in self.grid:
                        self.grid[key] = []
                    self.grid[key].append(block)
    
    def _get_blocks_in_area(self, x: float, y: float, radius: float) -> List[pygame.Rect]:
        """Get blocks near a position using spatial partitioning"""
        min_gx = floor((x - radius) / self.grid_size)
        max_gx = floor((x + radius) / self.grid_size)
        min_gy = floor((y - radius) / self.grid_size)
        max_gy = floor((y + radius) / self.grid_size)
        
        nearby_blocks = []
        for gx in range(min_gx, max_gx + 1):
            for gy in range(min_gy, max_gy + 1):
                if (gx, gy) in self.grid:
                    nearby_blocks.extend(self.grid[(gx, gy)])
        return nearby_blocks
    
    def _cast_ray_dda(self, origin: Tuple[float, float], angle: float) -> Tuple[float, float]:
        """Digital Differential Analyzer algorithm for ray casting"""
        x, y = origin
        ray_cos, ray_sin = cos(angle), sin(angle)
        
        # Unit step sizes
        step_x = 1 if ray_cos >= 0 else -1
        step_y = 1 if ray_sin >= 0 else -1
        
        # Initial distances to next grid lines
        t_delta_x = abs(1 / ray_cos) if ray_cos != 0 else float('inf')
        t_max_x = abs((floor(x) + (1 if step_x > 0 else 0) - x) / ray_cos) if ray_cos != 0 else float('inf')
        
        t_delta_y = abs(1 / ray_sin) if ray_sin != 0 else float('inf')
        t_max_y = abs((floor(y) + (1 if step_y > 0 else 0) - y) / ray_sin) if ray_sin != 0 else float('inf')
        
        current_distance = 0
        last_x, last_y = x, y
        
        while current_distance < self.view_distance:
            # Walk to next grid cell
            if t_max_x < t_max_y:
                last_x += step_x
                current_distance = t_max_x
                t_max_x += t_delta_x
            else:
                last_y += step_y
                current_distance = t_max_y
                t_max_y += t_delta_y
            
            # Check for collisions in this grid cell
            nearby_blocks = self._get_blocks_in_area(last_x, last_y, 1)
            
            for block in nearby_blocks:
                if (block.left <= last_x <= block.right and
                    block.top <= last_y <= block.bottom):
                    return ((last_x, last_y), [block])
        
        # No collision found
        end_x = x + ray_cos * self.view_distance
        end_y = y + ray_sin * self.view_distance
        return ((end_x, end_y),[])
    
    def calculate_fov(self, player_pos: Tuple[float, float], 
                    facing_angle: float = None, 
                    mouse_pos: Tuple[float, float] = None) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Calculate field of view rays.
        
        Args:
            player_pos: (x, y) position of player
            facing_angle: Optional fixed facing angle (radians)
            mouse_pos: Optional mouse position to face toward
            
        Returns:
            List of rays as ((start_x, start_y), (end_x, end_y))
            List of hit blocks
        """
        # Determine facing direction
        if mouse_pos is not None:
            dx = mouse_pos[0] - player_pos[0]
            dy = mouse_pos[1] - player_pos[1]
            center_angle = atan2(dy, dx)
        elif facing_angle is not None:
            center_angle = facing_angle
        else:
            center_angle = 0  # Default to right
        
        # Dynamic ray count based on distance to walls
        ray_count = min(self.base_ray_count + int(self.view_distance * self.ray_density), 200)
        
        # Convert FOV angle to radians and get half angle for spread
        half_fov = math.radians(self.fov_angle) / 2
        
        rays = []
        visible_blocks = []
        for i in range(ray_count):
            # Calculate angle for this ray
            # This spreads the rays evenly across the FOV angle
                   #facing         start of cone            fraction added to move    
            angle = center_angle - half_fov + (2 * half_fov * i / max(1, ray_count-1))
            
            # Cast ray using DDA algorithm
            end_point, hit_blocks = self._cast_ray_dda(player_pos, angle)
            rays.append((player_pos, end_point))
            for block in hit_blocks:
                if block not in visible_blocks:  # Manual duplicate check
                    visible_blocks.append(block)
            
        return rays, visible_blocks
    
    def update_blocks(self, new_blocks: List[pygame.Rect]):
        """Update the blocking geometry (call when level changes)"""
        self.blocks = new_blocks
        self._init_spatial_partition()
    
    def toggle_light(self):
        self.light_on = not self.light_on

    def create_light_flicker(self, lightframes: int, darkframes: int):
        # State management
        if self.dark:
            self.lightness_frames = 0
            self.darkness_frames += 1
        elif not self.dark:
            self.lightness_frames += 1
            self.darkness_frames = 0
        
        # State transitions with randomness
        if (self.lightness_frames >= random.randrange(lightframes, int(lightframes*1.2))):
            self.dark = True
        if (self.darkness_frames >= random.randrange(darkframes, int(darkframes*1.2))):
            self.dark = False
        
        # Enhanced flickering behavior
        if self.dark:
            # When dark, occasionally produce small flickers (40-70)
            if random.random() < 0.05:  # 5% chance of small flicker during dark phase

                return random.randrange(40, 70)
            return 0
        elif not self.dark:

            # When light, produce dramatic flickering (40-120)
            base = random.randrange(110, 120)
            return base
    def create_combined_lighting(self, size: Tuple[int, int], rays: List, player_pos: Tuple[float, float], lightframes: int=500, darkframes: int=100):
        """Optimized combined lighting with pre-allocation"""
        if not hasattr(self, '_combined_lighting') or size != self._combined_lighting.get_size():
            self._combined_lighting = pygame.Surface(size, pygame.SRCALPHA)
            self._light_cone = pygame.Surface(size, pygame.SRCALPHA)
            self._last_size = size
        
        # Clear surfaces
        self._combined_lighting.fill((0, 0, 0, 255))
        self._light_cone.fill((0, 0, 0, 0))
        if not self.light_on:
            return self._combined_lighting
        # Draw visibility polygon
        if len(rays) >= 3:
            points = [rays[0][1]]  # First ray end
            points.extend(end for _, end in rays[1:-1])  # Middle rays
            points.append(rays[-1][1])  # Last ray end
            
            # Draw directly to surfaces
            
            alpha = self.create_light_flicker(lightframes=lightframes, darkframes=darkframes)
            # actual visiblity (alpha = 0 visible)
            pygame.draw.polygon(self._combined_lighting, (0, 0, 0,  255-alpha), [player_pos] + points)
            # light cone only effect (alpha=255 visible)
            pygame.draw.polygon(self._light_cone, (255, 255, 255, alpha), [player_pos] + points) 
        
        # Combine
        self._combined_lighting.blit(self._light_cone, (0, 0))
        return self._combined_lighting
    def is_visible(self, viewer_pos, target_rect: pygame.Rect, facing_angle):
        """More accurate visibility check for rectangular objects"""
        # 1. Early exit if light is off
        if not self.light_on or self.dark:
            return False
        
        # 2. Check if target contains viewer (extremely close)
        if target_rect.collidepoint(viewer_pos):
            return True
        
        # 3. Check distance to target edges
        closest_dist = min(
            math.dist(viewer_pos, target_rect.topleft),
            math.dist(viewer_pos, target_rect.topright),
            math.dist(viewer_pos, target_rect.bottomleft),
            math.dist(viewer_pos, target_rect.bottomright)
        )
        if closest_dist > self.view_distance + target_rect.width:
            return False
        
        # 4. Enhanced angle check with object width compensation
        angle_to_center = math.atan2(
            target_rect.centery - viewer_pos[1],
            target_rect.centerx - viewer_pos[0]
        )
        angle_diff = (angle_to_center - facing_angle + math.pi) % (2*math.pi) - math.pi
        
        # Calculate angular width of the target
        target_angular_width = math.atan2(target_rect.width, closest_dist)
        half_fov = math.radians(self.fov_angle/2)
        
        if abs(angle_diff) > half_fov + target_angular_width/2:
            return False
        
        # 5. More thorough line-of-sight check
        return self._has_clear_line_of_sight(viewer_pos, target_rect)

    def _has_clear_line_of_sight(self, start_pos, target_rect):
        """More accurate line-of-sight check with multiple sampling"""
        # Check center and all four corners
        test_points = [
            target_rect.center,
            target_rect.topleft,
            target_rect.topright,
            target_rect.bottomleft,
            target_rect.bottomright
        ]
        
        # Also check midpoints of edges if object is large
        if target_rect.width > 32 or target_rect.height > 32:
            test_points.extend([
                (target_rect.left, target_rect.centery),
                (target_rect.right, target_rect.centery),
                (target_rect.centerx, target_rect.top),
                (target_rect.centerx, target_rect.bottom)
            ])
        
        for point in test_points:
            if self._check_single_line(start_pos, point):
                return True
        return False

    def _check_single_line(self, start, end):
        """Bresenham's line algorithm for pixel-perfect checking"""
        x0, y0 = map(int, start)
        x1, y1 = map(int, end)
        
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        
        while True:
            # Check if current point is in target
            if (x0, y0) == (x1, y1):
                return True
            
            # Check if we hit a wall
            for block in self._get_blocks_in_area(x0, y0, 1):
                if block.collidepoint(x0, y0):
                    return False
            
            e2 = 2 * err
            if e2 >= dy:
                if x0 == x1:
                    break
                err += dy
                x0 += sx
            if e2 <= dx:
                if y0 == y1:
                    break
                err += dx
                y0 += sy
        
        return True