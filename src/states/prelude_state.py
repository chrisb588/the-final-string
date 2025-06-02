from .prelude_substates.cutscene_state import CutsceneState
import pygame

class PreludeState:
    def __init__(self, surface):
        self.surface = surface
        self.cutscene = CutsceneState(self.surface)
        self.initialized = False

    def enter(self):
        """Called when entering the prelude state"""
        # return self.cutscene.enter('prelude')

    def update(self):
        """Update cutscene state"""
        pass

    def handle_event(self, event):
        """Handle input events"""
        pass

    def render(self):
        """Render current frame"""
        pass

    def exit(self):
        """Clean up resources"""
        pass