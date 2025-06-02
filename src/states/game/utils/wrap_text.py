import pygame

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """
    Wrap text to fit within max_width pixels
    
    Args:
        text: Text to wrap
        font: Font to use for measuring text width
        max_width: Maximum width in pixels
        
    Returns:
        List of wrapped lines
    """
    if not text.strip():
        return [text]
    
    # Handle explicit line breaks first
    paragraphs = text.split('\n')
    wrapped_lines = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            wrapped_lines.append('')
            continue
            
        words = paragraph.split(' ')
        current_line = ''
        
        for word in words:
            # Test if adding this word would exceed max width
            test_line = current_line + (' ' if current_line else '') + word
            text_width = font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                # If current line is not empty, save it and start new line
                if current_line:
                    wrapped_lines.append(current_line)
                    current_line = word
                else:
                    # Single word is too long, break it
                    wrapped_lines.append(word)
        
        # Add remaining text
        if current_line:
            wrapped_lines.append(current_line)
    
    return wrapped_lines