import pygame
import moderngl
import numpy as np
import time
from pygame.locals import DOUBLEBUF, OPENGL

class CRTFilter:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ctx = moderngl.create_context()
        self.time = 0

        self.prog = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;
            void main() {
                uv = in_uv;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            """,
            fragment_shader=self._fragment_shader()
        )

        vertices = np.array([
            -1, -1, 0, 0,
             1, -1, 1, 0,
            -1,  1, 0, 1,
             1,  1, 1, 1,
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_uv')
        self.texture = self.ctx.texture((width, height), 4)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])

    def render(self, surface):
        self.time += 0.01
        raw = pygame.image.tostring(surface, 'RGBA', True)
        self.texture.write(raw)
        self.texture.use()
        self.prog['time'].value = self.time
        self.ctx.clear(0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def _fragment_shader(self):
        return """
        #version 330
        uniform sampler2D tex;
        uniform float time;
        in vec2 uv;
        out vec4 fragColor;

        float rand(vec2 co) {
            return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
        }

        float noise(vec2 p) {
            return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453);
        }

        vec3 rgbShift(vec2 uv, float amount) {
            float r = texture(tex, uv + vec2(amount, 0.0)).r;
            float g = texture(tex, uv).g;
            float b = texture(tex, uv - vec2(amount, 0.0)).b;
            return vec3(r, g, b);
        }

        vec3 vignette(vec3 color, vec2 uv) {
            float dist = distance(uv, vec2(0.5, 0.5));
            float vignette = smoothstep(0.8, 0.4, dist);
            vignette = mix(1.0, vignette, 0.7);
            color *= vignette;
            return color;
        }

        vec3 scanlines(vec3 color, vec2 uv) {
            float scanline = sin(uv.y * 800.0) * 0.05;
            color -= scanline;
            return color;
        }

        vec3 staticEffect(vec3 color, vec2 uv, float amount) {
            float staticVal = rand(uv + time) * amount;
            color += staticVal;
            return color;
        }

        vec2 warpUV(vec2 uv) {
            // Reduced curvature with edge preservation
            vec2 centered = uv * 2.0 - 1.0;
            
            // Gentle curvature
            float curveStrength = 0.15;  // Reduced from 0.2
            centered.x *= 1.0 + curveStrength * pow(centered.y, 2.0);
            centered.y *= 1.0 + curveStrength * pow(centered.x, 2.0);
            
            // Radial distortion with edge clamping
            float radius = length(centered);
            float distortion = 0.15 * pow(radius, 2.0);  // Reduced from 0.2
            
            // Apply distortion while preserving edges
            vec2 distorted = centered * (1.0 + distortion);
            
            // Clamp to ensure we fill the screen
            distorted = clamp(distorted, -1.0, 1.0);
            
            return (distorted + 1.0) / 2.0;
        }

        vec3 horizontalWarp(vec3 color, vec2 uv) {
            float warp = sin(uv.y * 10.0 + time * 1.5) * 0.0015;
            color = texture(tex, vec2(uv.x + warp, uv.y)).rgb;
            return color;
        }

        void main() {
            // Warp the UV coordinates
            vec2 warpedUV = warpUV(uv);
            
            // Base color with subtle RGB shift
            vec3 color = rgbShift(warpedUV, 0.003 * (0.5 + 0.5 * sin(time * 0.3)));
            
            // Apply VHS effects
            color = horizontalWarp(color, warpedUV);
            color = scanlines(color, warpedUV);
            color = vignette(color, warpedUV);
            color = staticEffect(color, warpedUV, 0.03 * (0.5 + 0.5 * sin(time * 2.0)));
            
            // Add some noise
            float n = noise(warpedUV + time) * 0.01;
            color += n;
            
            fragColor = vec4(color, 1.0);
        }
        """

class Terminal:
    def __init__(self, font, max_lines=5):
        self.font = font
        self.lines = []
        self.max_lines = max_lines
        self.dot_count = 0
        self.last_update = 0
        self.update_interval = 300  # ms

    def add_line(self, text, animate_dots=False):
        if len(self.lines) >= self.max_lines:
            self.lines.pop(0)
        self.lines.append({"text": text, "animate_dots": animate_dots, "start_time": pygame.time.get_ticks()})

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.update_interval:
            self.dot_count = (self.dot_count + 1) % 4
            self.last_update = current_time

    def render(self, surface, pos):
        y_offset = 0
        for i, line in enumerate(self.lines):
            text = line["text"]
            if line["animate_dots"]:
                dots = "." * self.dot_count
                text += dots
            
            text_surface = self.font.render(text, True, (0, 255, 0))
            surface.blit(text_surface, (pos[0], pos[1] + y_offset))
            y_offset += self.font.get_height() + 5

def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 572), pygame.DOUBLEBUF | pygame.OPENGL)
    crt = CRTFilter(1024, 572)
    font = pygame.font.Font("assets/fonts/PixelSerif.ttf", 24)
    title_font = pygame.font.Font("assets/fonts/PixelSerif.ttf", 72)
    menu_font = pygame.font.Font("assets/fonts/PixelSerif.ttf", 48)
    
    terminal = Terminal(font)
    surface = pygame.Surface((1024, 572))
    
    # Game state
    STATE_LOADING = 0
    STATE_MENU = 1
    STATE_PLAYING = 2
    state = STATE_LOADING
    
    loading_stages = [
        ("Initializing systems", True),
        ("Generating levels", True),
        ("Loading assets", True),
        ("Finalizing setup", True)
    ]
    current_stage = 0
    stage_start_time = pygame.time.get_ticks()
    
    menu_items = ["Play", "Exit"]
    selected_item = 0
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == STATE_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_item = (selected_item + 1) % len(menu_items)
                    elif event.key == pygame.K_UP:
                        selected_item = (selected_item - 1) % len(menu_items)
                    elif event.key == pygame.K_RETURN:
                        if menu_items[selected_item] == "Play":
                            state = STATE_PLAYING
                            terminal.add_line("> Starting game...")
                        elif menu_items[selected_item] == "Exit":
                            running = False
        
        # Update
        terminal.update()
        
        if state == STATE_LOADING:
            if current_time - stage_start_time > 2000:  # 2 seconds per stage
                stage_start_time = current_time
                current_stage += 1
                if current_stage >= len(loading_stages):
                    state = STATE_MENU
                    terminal.add_line("> System ready")
                    terminal.add_line("> Welcome to THE FINAL STRING")
                else:
                    terminal.add_line(loading_stages[current_stage][0], loading_stages[current_stage][1])
        
        # Render
        surface.fill((10, 20, 10))
        
        if state == STATE_LOADING:
            pass  # Just show terminal output
        
        elif state == STATE_MENU:
            # Draw title
            title = title_font.render("THE FINAL STRING", True, (0, 255, 0))
            surface.blit(title, (1024//2 - title.get_width()//2, 100))
            
            # Draw menu items
            for i, item in enumerate(menu_items):
                color = (0, 255, 0) if i == selected_item else (0, 180, 0)
                prefix = "> " if i == selected_item else "  "
                item_text = menu_font.render(prefix + item, True, color)
                surface.blit(item_text, (1024//2 - item_text.get_width()//2, 250 + i * 60))
        
        elif state == STATE_PLAYING:
            # Draw playing message
            play_text = menu_font.render("Playing game...", True, (0, 255, 0))
            surface.blit(play_text, (1024//2 - play_text.get_width()//2, 250))
        
        # Draw terminal
        terminal.render(surface, (20, 572 - 150))
        
        # Apply CRT filter
        crt.render(surface)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()