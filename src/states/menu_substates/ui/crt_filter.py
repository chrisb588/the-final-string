import pygame
import moderngl
import numpy as np

class CRTFilter:
    """Applies a CRT screen effect using OpenGL shaders"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ctx = moderngl.create_context()
        self.time = 0

        # Create shader program
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

        # Create vertices for fullscreen quad
        vertices = np.array([
            -1, -1, 0, 0,  # Bottom-left
             1, -1, 1, 0,  # Bottom-right
            -1,  1, 0, 1,  # Top-left
             1,  1, 1, 1,  # Top-right
        ], dtype='f4')

        # Set up OpenGL buffers
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(
            self.prog, self.vbo, 'in_vert', 'in_uv'
        )
        self.texture = self.ctx.texture((width, height), 4)
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.texture]
        )

    def render(self, surface):
        """Render the CRT effect on the given surface"""
        self.time += 0.01
        # Convert Pygame surface to OpenGL texture
        raw = pygame.image.tostring(surface, 'RGBA', True)
        self.texture.write(raw)
        self.texture.use()
        
        # Update shader uniforms
        self.prog['time'].value = self.time
        
        # Render fullscreen quad with effect
        self.ctx.clear(0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def _fragment_shader(self):
        """Returns the GLSL fragment shader code"""
        return """
            #version 330
            uniform sampler2D tex;
            uniform float time;
            in vec2 uv;
            out vec4 fragColor;

            float rand(vec2 co) {
                return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
            }

            vec3 rgbShift(vec2 uv, float amount) {
                float r = texture(tex, uv + vec2(amount, 0.0)).r;
                float g = texture(tex, uv).g;
                float b = texture(tex, uv - vec2(amount, 0.0)).b;
                return vec3(r, g, b);
            }

            vec2 crtWarp(vec2 uv) {
                vec2 cc = uv - 0.5;
                float dist = dot(cc, cc) * 0.3;
                return uv + cc * (0.5 + dist) * dist;
            }

            // Add horizontal distortion function
            vec2 horizontalDistort(vec2 uv) {
                // Create a moving wave effect
                float wave = sin(uv.y * 10.0 + time * 2.0) * 0.001;
                // Add some random jitter to make it more organic
                wave += rand(vec2(time, uv.y)) * 0.0005;
                return vec2(uv.x + wave, uv.y);
            }

            void main() {
                // Apply CRT warping
                vec2 warpedUV = crtWarp(uv);

                 warpedUV = horizontalDistort(warpedUV);
                
                // RGB shift effect
                vec3 color = rgbShift(warpedUV, 0.001);
                
                // Scanline effect
                float scanline = sin(warpedUV.y * 800.0) * 0.04;
                color -= scanline;
                
                // Vignette
                float vignette = length(vec2(0.5) - warpedUV);
                color *= 1.0 - vignette * 0.8;
                
                // Static noise
                float noise = rand(uv + time) * 0.1;
                color += noise * 0.1;
                
                fragColor = vec4(color, 1.0);
            }
        """