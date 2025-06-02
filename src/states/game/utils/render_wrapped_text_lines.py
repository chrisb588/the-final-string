import pygame

def render_wrapped_text_lines(screen: pygame.Surface, lines: list[str], font: pygame.font.Font, 
                             color: tuple, start_x: int, start_y: int, line_spacing: int = 3) -> int:
    """
    Render a list of wrapped text lines
    
    Args:
        screen: Surface to render to
        lines: List of text lines to render
        font: Font to use
        color: Text color
        start_x: Starting X position
        start_y: Starting Y position
        line_spacing: Extra spacing between lines
        
    Returns:
        The Y position after the last line
    """
    current_y = start_y
    line_height = font.get_height()
    
    for line in lines:
        if line.strip():  # Only render non-empty lines
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (start_x, current_y))
        current_y += line_height + line_spacing
    
    return current_y