import pygame
import os
from .password_judge import PasswordUI
from .rules_count import RulesCount
from .dialogue_box import DialogueBox
from .compass import Compass
from .hud import HUD
from .pause_button import PauseButton
from .popup_notification import PopupNotification

class UIManager:
    """Manages all UI components and their interactions"""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize UI manager with screen surface"""
        if not isinstance(screen, pygame.Surface):
            raise ValueError("Screen must be a pygame Surface")
            
        self.screen = screen
        self._init_components()
        
    def _init_components(self):
        """Initialize all UI components in rendering order"""
        try:
            # Set initial states
            self.show_debug = False
            self.show_coordinates = False
            self.show_speed_debug = False
            
            # Initialize password UI first as other components may depend on it
            self.password_ui = PasswordUI(self.screen)
            
            # Initialize other components
            self.dialogue_box = DialogueBox(self.screen, ui_manager=self.password_ui)
            self.rules_ui = RulesCount(self.screen, ui_manager=self.password_ui)
            self.compass = Compass(self.screen)
            self.compass.show_speed_debug = self.show_speed_debug
            self.hud = HUD(self.screen)
            self.pause_button = PauseButton(self.screen)
            self.popup = PopupNotification(self.screen)
            
        except Exception as e:
            print(f"Error initializing UI components: {e}")
            raise

    def show_popup(self, message: str, duration: int = 2000):
        """Show a popup notification"""
        self.popup.show(message, duration)
            
    def show_message(self, message: str, duration: int = 2000):
        """Display a temporary message"""
        try:
            self.dialogue_box.show_message(message, duration)
        except Exception as e:
            print(f"Error showing message: {e}")
            
    def update(self, delta_time: float):
        """Update all UI components"""
        try:
            self.popup.update()
            self.dialogue_box.update()
            self.password_ui.update(delta_time)
            if hasattr(self.rules_ui, 'update'):
                self.rules_ui.update(delta_time)
            if hasattr(self.password_ui, 'rules_text') and self.password_ui.rules_text is not None:
                self.password_ui.rules_text.update(delta_time)
        except Exception as e:
            print(f"Error updating UI: {e}")
            
    def render(self, game_data: dict):
        """Render all UI components"""
        try:
            # Render HUD elements
            if self.show_speed_debug:
                self.hud.draw_speed_indicator(game_data.get('player_speed', 0))
            self.hud.draw_zoom_indicator(game_data.get('camera_zoom', 1.0))

            # Render compass if we have door data
            nearest_door = game_data.get('nearest_door')
            if nearest_door:
                self.compass.draw(
                    nearest_door,
                    game_data.get('door_angle', 0)
                )

            self.hud.render()
                
            # Render interactive UI elements
            self.dialogue_box.render()
            self.rules_ui.render(
                game_data.get('current_rules', []),
                game_data.get('total_rules', None)
            )
            self.password_ui.render()
            
            # Render pause button if game is paused
            if game_data.get('paused', False):
                self.pause_button.draw(paused=True)
                
            # Render debug info if enabled
            if self.show_coordinates:
                self._render_debug_info(game_data)

            self.popup.render()
                
        except Exception as e:
            print(f"Error rendering UI: {e}")
            
    def _render_debug_info(self, game_data: dict):
        """Render debug information when enabled"""
        try:
            if hasattr(self.hud, 'draw_debug_info'):
                self.hud.draw_debug_info(
                    player_pos=game_data.get('player_pos'),
                    mouse_pos=game_data.get('mouse_pos'),
                    fps=game_data.get('fps'),
                    additional_info=game_data.get('debug_info', {})
                )
        except Exception as e:
            print(f"Error rendering debug info: {e}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI-related events"""
        try:
            # Always allow fullscreen toggle
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT) or \
                event.key == pygame.K_F11:
                    return False  # Let the main game handle fullscreen toggle
            
            # If dialogue box is active, only handle its events and fullscreen
            if self.dialogue_box.is_active:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    if not self.dialogue_box.typing_complete:
                        self.dialogue_box.complete_typing()
                        return True
                    else:
                        self.dialogue_box.hide()
                        return True 
                return True
            
            # Handle other UI events as normal
            if self.password_ui.handle_event(event):
                return True
                
            # Let rules UI handle events next
            if hasattr(self.rules_ui, 'handle_event'):
                if self.rules_ui.handle_event(event):
                    return True
                    
            return False
                
        except Exception as e:
            print(f"Error handling UI event: {e}")
            return False
        
    def show(self, rules: list[str], door, callback: callable = None, collected_rules: list[str] = None, 
         preserved_password: str = "", close_callback: callable = None):
        """Show the password UI with rules"""
        self.password_ui.show(
            rules=rules,
            door=door,
            callback=callback,
            collected_rules=collected_rules,
            preserved_password=preserved_password,
            close_callback=close_callback
        )
            
    def set_debug_flags(self, show_debug: bool = None, show_coordinates: bool = None, 
                       show_speed_debug: bool = None):
        """Update debug visibility flags"""
        if show_debug is not None:
            self.show_debug = show_debug
        if show_coordinates is not None:
            self.show_coordinates = show_coordinates
            self.hud.show_coordinates = show_coordinates
        if show_speed_debug is not None:
            self.show_speed_debug = show_speed_debug
            self.hud.show_speed_debug = show_speed_debug
            self.compass.show_speed_debug = show_speed_debug