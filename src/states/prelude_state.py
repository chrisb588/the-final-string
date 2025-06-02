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
        return self.cutscene.update()

    def handle_event(self, event):
        """Handle input events"""
        return self.cutscene.handle_event(event)

    def render(self, surface):
        """Render current frame"""
        if self.cutscene.video_manager.is_playing:
            self.cutscene.render(surface)

    def exit(self):
        """Clean up resources"""
        self.cutscene.exit()