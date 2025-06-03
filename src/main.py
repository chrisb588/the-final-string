import os
import sys
import pygame
from pygame.locals import DOUBLEBUF
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH

from states.menu_state import Menu
from states.game_state import GameDemo
from states.prelude_state import PreludeState
from states.end_state import EndState
from pyvidplayer2 import Video

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.is_fullscreen = False
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Initialize single screen without OpenGL
        self.screen = pygame.display.set_mode(self.windowed_size, DOUBLEBUF)
        pygame.display.set_caption("The Final String")
        
        # Initialize states (don't create GameDemo yet - create when needed)
        menu = Menu(self.screen)
        prelude = PreludeState(self.screen)
        end = EndState()

        # Load background music
        self.menu_bgm = pygame.mixer.Sound('assets/audio/menu_bgm.mp3')
        self.game_bgm = pygame.mixer.Sound('assets/audio/bgm.mp3')
        self.menu_bgm.set_volume(0.1)
        self.game_bgm.set_volume(0.1)
        self.menu_bgm.play(loops=-1)  # Start with menu music 
        
        self.states = {
            'menu': menu,
            'prelude': prelude,
            'end': end
        }
        
        self.current_state = 'menu'
        self.clock = pygame.time.Clock()
        self.running = True
        self.vid1 = None  # Initialize video as None - load when needed
        self.vid2 = None  # Initialize video as None - load when needed
        self.skip_font = pygame.font.Font(FONT_PATH, 24)

    def apply_scanline_effect(self, surface):
        """Apply a simple scanline effect using pure Pygame"""
        # Create a surface for the scanlines
        scanline_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        scanline_surface.set_alpha(30)  # Make it semi-transparent
        
        # Draw horizontal lines every 2 pixels for scanline effect
        for y in range(0, SCREEN_HEIGHT, 2):
            pygame.draw.line(scanline_surface, (0, 0, 0), (0, y), (SCREEN_WIDTH, y))
        
        # Blit the scanline overlay onto the main surface
        surface.blit(scanline_surface, (0, 0))

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h),
                DOUBLEBUF | pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode(
                self.windowed_size,
                DOUBLEBUF
            )

    def render_frame(self):
        """Handle the complete rendering pipeline"""
        if self.current_state == 'prelude':
            # Handle prelude video - no effects for videos
            if self.vid1 and self.vid1.active:
                # Clear the screen
                self.screen.fill((0, 0, 0))
                
                # Get video dimensions
                video_width = self.vid1.current_size[0]
                video_height = self.vid1.current_size[1]
                
                # Calculate scaling to maintain aspect ratio
                screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
                video_ratio = video_width / video_height
                
                if video_ratio > screen_ratio:
                    # Video is wider than screen ratio - fit to width
                    scaled_width = SCREEN_WIDTH
                    scaled_height = int(SCREEN_WIDTH / video_ratio)
                else:
                    # Video is taller than screen ratio - fit to height
                    scaled_height = SCREEN_HEIGHT
                    scaled_width = int(SCREEN_HEIGHT * video_ratio)
                
                # Center the video
                x_pos = (SCREEN_WIDTH - scaled_width) // 2
                y_pos = (SCREEN_HEIGHT - scaled_height) // 2
                
                # Create a temporary surface for the video
                temp_surface = pygame.Surface((video_width, video_height))
                self.vid1.draw(temp_surface, (0, 0), force_draw=True)
                
                # Scale and position the video
                if scaled_width != video_width or scaled_height != video_height:
                    scaled_surface = pygame.transform.scale(temp_surface, (scaled_width, scaled_height))
                else:
                    scaled_surface = temp_surface
                
                # Blit the scaled video to the center of the screen
                self.screen.blit(scaled_surface, (x_pos, y_pos))
                
                skip_text = self.skip_font.render("Press SPACE to skip", True, (200, 200, 200))
                skip_rect = skip_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
                self.screen.blit(skip_text, skip_rect)
                
                # Use regular pygame display update for videos
                pygame.display.flip()
                
                # Check if video ended naturally
                if not self.vid1.active:
                    self.change_state('game')
            else:
                # Video failed to load or ended, go to game
                self.change_state('game')
        elif self.current_state == 'end':
            # Handle end video - also no effects
            if self.vid2 and self.vid2.active:
                # Clear the screen
                self.screen.fill((0, 0, 0))
                
                # Get video dimensions
                video_width = self.vid2.current_size[0]
                video_height = self.vid2.current_size[1]
                
                # Calculate scaling to maintain aspect ratio
                screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
                video_ratio = video_width / video_height
                
                if video_ratio > screen_ratio:
                    # Video is wider than screen ratio - fit to width
                    scaled_width = SCREEN_WIDTH
                    scaled_height = int(SCREEN_WIDTH / video_ratio)
                else:
                    # Video is taller than screen ratio - fit to height
                    scaled_height = SCREEN_HEIGHT
                    scaled_width = int(SCREEN_HEIGHT * video_ratio)
                
                # Center the video
                x_pos = (SCREEN_WIDTH - scaled_width) // 2
                y_pos = (SCREEN_HEIGHT - scaled_height) // 2
                
                # Create a temporary surface for the video
                temp_surface = pygame.Surface((video_width, video_height))
                self.vid2.draw(temp_surface, (0, 0), force_draw=True)
                
                # Scale and position the video
                if scaled_width != video_width or scaled_height != video_height:
                    scaled_surface = pygame.transform.scale(temp_surface, (scaled_width, scaled_height))
                else:
                    scaled_surface = temp_surface
                
                # Blit the scaled video to the center of the screen
                self.screen.blit(scaled_surface, (x_pos, y_pos))
                
                skip_text = self.skip_font.render("Press SPACE to skip", True, (200, 200, 200))
                skip_rect = skip_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
                self.screen.blit(skip_text, skip_rect)
                
                # Use regular pygame display update for videos
                pygame.display.flip()
                
                # Check if video ended naturally
                if not self.vid2.active:
                    self.change_state('menu')
            else:
                # Video failed to load or ended, go to menu
                self.change_state('menu')
        else:
            # Render other states normally (menu, etc.)
            self.screen.fill((0, 0, 0))
            if self.current_state in self.states and hasattr(self.states[self.current_state], 'render'):
                self.states[self.current_state].render()
            
            # Apply simple scanline effect ONLY for menu state
            if self.current_state == 'menu':
                self.apply_scanline_effect(self.screen)
            
            pygame.display.flip()

    def run_game_state(self):
        """Let GameDemo take control but use our existing screen"""
        print("Starting game with existing windowed screen...")
        
        # Create GameDemo instance that uses our existing screen
        game_demo = GameDemo(screen=self.screen)
        
        # Let GameDemo run its own complete game loop
        game_demo.run()
        
        # Check if the game was completed (level-4 finished)
        if hasattr(game_demo, 'game_completed') and game_demo.game_completed:
            print("Game completed! Transitioning to end video...")
            self.change_state('end')  # Use change_state to properly load the video
        else:
            # When GameDemo exits normally, return to menu (screen stays the same)
            print("GameDemo exited, returning to main menu...")
            self.change_state('menu')  # Use change_state for consistency

    def run(self):
        try:
            # Enter initial state
            if hasattr(self.states[self.current_state], 'enter'):
                self.states[self.current_state].enter()

            while self.running:
                # Special handling for game state - let GameDemo take over completely
                if self.current_state == 'game':
                    self.run_game_state()
                    continue  # After game exits, continue with main loop
                
                # Handle global events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        continue

                    if self.current_state == 'prelude' and event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if self.vid1:
                                self.vid1.close()
                            self.change_state('game')  # Skip to game state
                            continue

                    if self.current_state == 'end' and event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if self.vid2:
                                self.vid2.close()
                            self.change_state('menu')  # Skip to menu
                            continue
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F11:
                            self.toggle_fullscreen()
                    
                    # Handle other state-specific events (menu, etc.)
                    if self.current_state in self.states and hasattr(self.states[self.current_state], 'handle_event'):
                        next_state = self.states[self.current_state].handle_event(event)
                        if next_state:
                            self.change_state(next_state)

                # Update current state
                if self.current_state in self.states and hasattr(self.states[self.current_state], 'update'):
                    next_state = self.states[self.current_state].update()
                    if next_state:
                        self.change_state(next_state)
                
                self.render_frame()
                
                # Control frame rate for non-game states (game has its own timing)
                if self.current_state != 'game':
                    if self.current_state in ['prelude', 'end']:
                        # For video states, use video timing
                        pygame.time.wait(16)  # ~60 FPS
                    else:
                        # For other states, use normal clock
                        self.clock.tick(60)
            
            # Exit final state
            if self.current_state in self.states and hasattr(self.states[self.current_state], 'exit'):
                self.states[self.current_state].exit()
        finally:
            self.bgm.stop()
            pygame.mixer.quit()
            pygame.quit()
            sys.exit()

    def change_state(self, new_state):
        """Handle state transitions"""
        if new_state in self.states or new_state == 'game':
            # Clean up previous state
            if self.current_state in self.states and hasattr(self.states[self.current_state], 'exit'):
                self.states[self.current_state].exit()
            
            # Handle BGM transitions
            if new_state == 'menu':
                self.game_bgm.stop()
                self.menu_bgm.play(loops=-1)
            elif new_state == 'game':
                self.menu_bgm.stop()
                self.game_bgm.play(loops=-1)
            elif new_state in ['prelude', 'end']:
                self.menu_bgm.stop()
                self.game_bgm.stop()

            # Handle video initialization/cleanup
            if new_state == 'prelude':
                try:
                    self.vid1 = Video('assets/video/cutscenes/prelude.mp4')
                except Exception as e:
                    print(f"Failed to load prelude video: {e}")
                    # If video fails to load, skip to game
                    new_state = 'game'
            elif new_state == 'end':
                try:
                    self.vid2 = Video('assets/video/cutscenes/epilogue.mp4')
                except Exception as e:
                    print(f"Failed to load end video: {e}")
                    # If video fails to load, skip to menu
                    new_state = 'menu'
            elif self.current_state == 'prelude':
                if self.vid1:
                    self.vid1.close()
                    self.vid1 = None
            elif self.current_state == 'end':
                if self.vid2:
                    self.vid2.close()
                    self.vid2 = None
            
            self.current_state = new_state
            
            # Only call enter for non-game states (game state handles its own initialization)
            if new_state != 'game' and new_state in self.states and hasattr(self.states[self.current_state], 'enter'):
                self.states[self.current_state].enter()

if __name__ == "__main__":
    game = Game()
    game.run()