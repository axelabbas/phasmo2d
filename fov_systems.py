import math
import pygame

class RadialFOVSystem():
    def __init__(self, view_distance: int, fov_angle: int=90):
        self.view_distance = view_distance
        self.fov_angle = fov_angle
    def draw_fov_polygon(self, size: tuple[int, int], viewer_pos: tuple[int,int], facing_angle: int):
        """Draws the FOV area as a polygon."""
        fov_surface = pygame.Surface(size, pygame.SRCALPHA)
        half_fov = math.radians(self.fov_angle / 2)
        
        # Calculate left and right boundary angles
        left_angle = facing_angle - half_fov
        right_angle = facing_angle + half_fov
        
        # Define the polygon points (viewer position + far points)
        polygon_points = [viewer_pos]
        
        # Number of segments for smoothness
        num_segments = 10  
        for i in range(num_segments + 1):
            angle = left_angle + (right_angle - left_angle) * (i / num_segments)
            end_x = viewer_pos[0] + math.cos(angle) * self.view_distance
            end_y = viewer_pos[1] + math.sin(angle) * self.view_distance
            polygon_points.append((end_x, end_y))
        
        # Draw the FOV polygon
        pygame.draw.polygon(fov_surface, (255, 255, 0, 100), polygon_points) 
        return fov_surface
    def is_visible(self, viewer_pos, target_rect: pygame.Rect, facing_angle):
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
        if closest_dist > self.view_distance - target_rect.width:
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
            
            # # Check if we hit a wall
            # for block in self._get_blocks_in_area(x0, y0, 1):
            #     if block.collidepoint(x0, y0):
            #         return False
            
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