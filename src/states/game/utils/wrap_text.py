import pygame

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """
    Wrap text to fit within max_width pixels, handling text without spaces
    """
    if not text.strip():
        return [text]
    
    paragraphs = text.split('\n')
    wrapped_lines = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            wrapped_lines.append('')
            continue
            
        current_line = []
        remaining_width = max_width
        
        # Process each character individually
        for char in paragraph:
            char_width = font.size(char)[0]
            
            if char_width <= remaining_width:
                current_line.append(char)
                remaining_width -= char_width
            else:
                # Save current line and start a new one
                wrapped_lines.append(''.join(current_line))
                current_line = [char]
                remaining_width = max_width - char_width
        
        # Add remaining characters
        if current_line:
            wrapped_lines.append(''.join(current_line))
    
    return wrapped_lines