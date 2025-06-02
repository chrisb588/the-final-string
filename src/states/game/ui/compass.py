import pygame
import math
import os

class Compass:
    """Manages the compass UI element that points to the nearest door"""
    
    def __init__(self, screen):
        if screen is None:
            raise ValueError("Screen surface cannot be None")
        self.screen = screen
        self.show_speed_debug = False
        self.pixel_scale = 2
        self.compass_area_size = 64
        self._init_font()

    def _init_font(self):
        """Initialize font with fallback"""
        try:
            # Get the current file's directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Navigate to the main directory (4 levels up from current file)
            main_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
            
            # Construct path to font in assets directory
            font_path = os.path.join(main_dir, 'assets', 'fonts', 'UnifontEX.ttf')
            
            # Load font with error handling
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 32)
            else:
                print(f"Warning: Font file not found at {font_path}")
                self.font = pygame.font.Font(None, 32)
        except (pygame.error, IOError) as e:
            print(f"Warning: Could not initialize PauseButton font: {e}")
            self.font = pygame.font.SysFont('arial', 32)
        
    def update_position(self, base_y_offset=0):
        """Update compass position based on screen properties"""
        self.base_compass_x = self.screen.get_width() - self.compass_area_size - 15
        self.base_compass_y = 85 + base_y_offset
        self.center_x = self.base_compass_x + self.compass_area_size // 2
        self.center_y = self.base_compass_y + self.compass_area_size // 2

    def draw(self, nearest_door=None, angle=0):
        """Draw the compass with optional door direction"""
        self.update_position(35 if self.show_speed_debug else 0)
        
        # Draw compass body
        self._draw_compass_body()
        
        if nearest_door:
            self._draw_door_needle(angle)
            self._draw_label("DOOR")
        else:
            self._draw_cardinal_markers()
            self._draw_label("COMPASS")

    def _draw_compass_body(self):
        """Draw the basic compass body"""
        radius_pixels = 15
        body_color_dark = (30, 30, 30)
        body_color_mid = (50, 50, 50)
        body_color_light = (80, 80, 80)
        border_color = (120, 120, 120)

        for y_offset_px in range(-radius_pixels -1, radius_pixels + 2):
            for x_offset_px in range(-radius_pixels -1, radius_pixels + 2):
                dist_sq = x_offset_px**2 + y_offset_px**2
                px = self.center_x + x_offset_px * self.pixel_scale
                py = self.center_y + y_offset_px * self.pixel_scale

                if radius_pixels**2 <= dist_sq < (radius_pixels + 1.5)**2:
                    pygame.draw.rect(self.screen, border_color, 
                                  (px, py, self.pixel_scale, self.pixel_scale))
                elif dist_sq < radius_pixels**2:
                    if x_offset_px < -radius_pixels * 0.5 and y_offset_px < -radius_pixels * 0.5:
                        color = body_color_dark
                    elif x_offset_px > radius_pixels * 0.5 and y_offset_px > radius_pixels * 0.5:
                        color = body_color_light
                    else:
                        color = body_color_mid
                    pygame.draw.rect(self.screen, color, 
                                  (px, py, self.pixel_scale, self.pixel_scale))

        # Inner ring
        inner_ring_color = (70, 70, 70)
        for i_px in range(-radius_pixels, radius_pixels + 1):
            if abs(i_px * self.pixel_scale) < radius_pixels * self.pixel_scale * 0.7:
                pygame.draw.rect(self.screen, inner_ring_color,
                               (self.center_x + i_px * self.pixel_scale - self.pixel_scale//2,
                                self.center_y - self.pixel_scale//2,
                                self.pixel_scale, self.pixel_scale))
                pygame.draw.rect(self.screen, inner_ring_color,
                               (self.center_x - self.pixel_scale//2,
                                self.center_y + i_px * self.pixel_scale - self.pixel_scale//2,
                                self.pixel_scale, self.pixel_scale))

    def _draw_door_needle(self, angle):
        """Draw the needle pointing to the nearest door"""
        needle_color_main = (255, 50, 50)
        needle_color_accent = (200, 0, 0)
        needle_tail_color_main = (220, 220, 220)
        needle_tail_color_accent = (170, 170, 170)
        
        needle_front_len_px = 10
        needle_tail_len_px = 6

        # Draw main needle
        for i in range(needle_front_len_px):
            dist = i * self.pixel_scale
            px = self.center_x + math.cos(angle) * dist
            py = self.center_y + math.sin(angle) * dist
            pygame.draw.rect(self.screen, needle_color_accent,
                           (px - self.pixel_scale + self.pixel_scale//2,
                            py - self.pixel_scale + self.pixel_scale//2,
                            self.pixel_scale*2, self.pixel_scale*2))
            pygame.draw.rect(self.screen, needle_color_main,
                           (px - self.pixel_scale, py - self.pixel_scale,
                            self.pixel_scale*2, self.pixel_scale*2))

        # Draw arrowhead
        self._draw_arrowhead(angle, needle_front_len_px)
        
        # Draw needle tail
        self._draw_needle_tail(angle, needle_tail_len_px)

        # Draw center pivot
        self._draw_center_pivot()

    def _draw_arrowhead(self, angle, needle_len):
        """Draw the arrowhead of the compass needle"""
        needle_color_main = (255, 50, 50)
        needle_color_accent = (200, 0, 0)
        
        tip_dist = needle_len * self.pixel_scale
        tip_x = self.center_x + math.cos(angle) * tip_dist
        tip_y = self.center_y + math.sin(angle) * tip_dist

        arrowhead_size_px = 3
        for i_arrow in range(-arrowhead_size_px // 2 + 1, arrowhead_size_px // 2 + 2):
            offset_angle = angle + math.pi / 2
            offset_dist = i_arrow * self.pixel_scale
            base_ax = (self.center_x + math.cos(angle) * (tip_dist - 2*self.pixel_scale) 
                      + math.cos(offset_angle) * offset_dist)
            base_ay = (self.center_y + math.sin(angle) * (tip_dist - 2*self.pixel_scale) 
                      + math.sin(offset_angle) * offset_dist)
            
            pygame.draw.rect(self.screen, needle_color_accent,
                           (base_ax-self.pixel_scale+self.pixel_scale//2,
                            base_ay-self.pixel_scale+self.pixel_scale//2,
                            self.pixel_scale*2, self.pixel_scale*2))
            pygame.draw.rect(self.screen, needle_color_main,
                           (base_ax-self.pixel_scale, base_ay-self.pixel_scale,
                            self.pixel_scale*2, self.pixel_scale*2))

        pygame.draw.rect(self.screen, needle_color_accent,
                        (tip_x-self.pixel_scale+self.pixel_scale//2,
                         tip_y-self.pixel_scale+self.pixel_scale//2,
                         self.pixel_scale*2, self.pixel_scale*2))
        pygame.draw.rect(self.screen, needle_color_main,
                        (tip_x-self.pixel_scale, tip_y-self.pixel_scale,
                         self.pixel_scale*2, self.pixel_scale*2))

    def _draw_needle_tail(self, angle, tail_length):
        """Draw the tail of the compass needle"""
        needle_tail_color_main = (220, 220, 220)
        needle_tail_color_accent = (170, 170, 170)

        for i in range(1, tail_length + 1):
            dist = i * self.pixel_scale
            base_tail_x = self.center_x + math.cos(angle + math.pi) * dist
            base_tail_y = self.center_y + math.sin(angle + math.pi) * dist

            # Draw main tail pixels
            px1 = base_tail_x + math.cos(angle + math.pi/2) * (self.pixel_scale / 2)
            py1 = base_tail_y + math.sin(angle + math.pi/2) * (self.pixel_scale / 2)
            pygame.draw.rect(self.screen, needle_tail_color_main,
                           (px1 - self.pixel_scale//2, py1 - self.pixel_scale//2,
                            self.pixel_scale, self.pixel_scale))
            
            px2 = base_tail_x - math.cos(angle + math.pi/2) * (self.pixel_scale / 2)
            py2 = base_tail_y - math.sin(angle + math.pi/2) * (self.pixel_scale / 2)
            pygame.draw.rect(self.screen, needle_tail_color_main,
                           (px2 - self.pixel_scale//2, py2 - self.pixel_scale//2,
                            self.pixel_scale, self.pixel_scale))
            
            # Add accent
            if i > 1:
                accent_tail_x = base_tail_x + self.pixel_scale//4
                accent_tail_y = base_tail_y + self.pixel_scale//4
                pygame.draw.rect(self.screen, needle_tail_color_accent,
                               (accent_tail_x - self.pixel_scale//2,
                                accent_tail_y - self.pixel_scale//2,
                                self.pixel_scale, self.pixel_scale))

    def _draw_center_pivot(self):
        """Draw the center pivot point of the compass"""
        pygame.draw.rect(self.screen, (80, 80, 80),
                        (self.center_x - self.pixel_scale,
                         self.center_y - self.pixel_scale,
                         self.pixel_scale*2, self.pixel_scale*2))
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (self.center_x - self.pixel_scale//2,
                         self.center_y - self.pixel_scale//2,
                         self.pixel_scale, self.pixel_scale))

    def _draw_cardinal_markers(self):
        """Draw cardinal direction markers when no door is present"""
        dir_color_cardinal = (200, 200, 200)
        dir_color_inter = (140, 140, 140)
        marker_len_px = 3
        radius_pixels = 15

        # Cardinal markers
        for i in range(marker_len_px):
            dist_from_edge = i * self.pixel_scale
            # N
            pygame.draw.rect(self.screen, dir_color_cardinal,
                           (self.center_x - self.pixel_scale//2,
                            self.base_compass_y + (radius_pixels - 12)*self.pixel_scale + dist_from_edge,
                            self.pixel_scale, self.pixel_scale))
            # S
            pygame.draw.rect(self.screen, dir_color_cardinal,
                           (self.center_x - self.pixel_scale//2,
                            self.base_compass_y + (radius_pixels + 10)*self.pixel_scale - dist_from_edge - self.pixel_scale*2,
                            self.pixel_scale, self.pixel_scale))
            # E
            pygame.draw.rect(self.screen, dir_color_cardinal,
                           (self.base_compass_x + (radius_pixels + 10)*self.pixel_scale - dist_from_edge - self.pixel_scale*2,
                            self.center_y - self.pixel_scale//2,
                            self.pixel_scale, self.pixel_scale))
            # W
            pygame.draw.rect(self.screen, dir_color_cardinal,
                           (self.base_compass_x + (radius_pixels - 12)*self.pixel_scale + dist_from_edge,
                            self.center_y - self.pixel_scale//2,
                            self.pixel_scale, self.pixel_scale))

        # Intercardinal markers
        inter_dist_factor = 0.707 * (radius_pixels - 1)
        inter_marker_positions = [
            (self.center_x + inter_dist_factor * self.pixel_scale,
             self.center_y - inter_dist_factor * self.pixel_scale),
            (self.center_x + inter_dist_factor * self.pixel_scale,
             self.center_y + inter_dist_factor * self.pixel_scale),
            (self.center_x - inter_dist_factor * self.pixel_scale,
             self.center_y + inter_dist_factor * self.pixel_scale),
            (self.center_x - inter_dist_factor * self.pixel_scale,
             self.center_y - inter_dist_factor * self.pixel_scale),
        ]
        
        for pos_x, pos_y in inter_marker_positions:
            pygame.draw.rect(self.screen, dir_color_inter,
                           (pos_x - self.pixel_scale//2,
                            pos_y - self.pixel_scale//2,
                            self.pixel_scale, self.pixel_scale))

        self._draw_center_pivot()

    def _draw_label(self, text):
        """Draw the compass label"""
        label_surface = self.font.render(text, True, (230, 230, 230) if text == "DOOR" else (180, 180, 180))
        label_rect = label_surface.get_rect(
            centerx=self.center_x,
            y=self.base_compass_y + self.compass_area_size + 3
        )
        outline_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(outline_surface, (label_rect.x + 1, label_rect.y + 1))
        self.screen.blit(label_surface, label_rect)