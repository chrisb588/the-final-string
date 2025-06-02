class EndState:
    def __init__(self):
        self.is_active = False
    
    def enter(self):
        self.is_active = True
    
    def exit(self):
        self.is_active = False
    
    def handle_event(self, event):
        # Handle end state events
        pass
    
    def update(self):
        # Update end state logic
        pass
    
    def render(self):
        # Render end state
        pass