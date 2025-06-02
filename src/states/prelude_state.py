import pygame

class PreludeState:
    def __init__(self):
        self.is_active = False
    
    def enter(self):
        self.is_active = True
        print("Entering prelude state...")  # Debug message
    
    def exit(self):
        self.is_active = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'menu'  # Allow returning to menu with ESC
        return None
    
    def update(self):
        # Update prelude state logic
        pass
    
    def render(self):
        # Render prelude state (placeholder)
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))  # Black background