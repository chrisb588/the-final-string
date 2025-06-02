import pygame
import moderngl
import numpy as np

class CRTFilter:
    """Optimized CRT screen effect using OpenGL shaders"""
    
    def __init__(self, width, height):
        # Create shared context only once
        if not hasattr(CRTFilter, '_ctx'):
            CRTFilter._ctx = moderngl.create_context()
        self.ctx = CRTFilter._ctx
        
        self.width = width
        self.height = height
        self.time = 0
        
        # Simplified vertex shader
        vertex_shader = """
            #version 330
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;
            void main() {
                uv = in_uv;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        """
        
        # Create shader program with optimized fragment shader
        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=self._optimized_fragment_shader()
        )

        # Create vertices for fullscreen quad (using triangle strip)
        vertices = np.array([
            -1, -1, 0, 0,
             1, -1, 1, 0,
            -1,  1, 0, 1,
             1,  1, 1, 1,
        ], dtype='f4')

        # Set up static OpenGL buffers
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_uv')
        
        # Create texture with optimized parameters
        self.texture = self.ctx.texture(
            (width, height), 
            4,  # RGBA
            dtype='f1'  # Use unsigned byte for better performance
        )
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.texture.swizzle = 'BGRA'  # Match pygame's format
        
        # Create framebuffer
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])

    def resize(self, width, height):
        """Handle resolution changes"""
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            # Recreate texture with new dimensions
            self.texture.release()
            self.texture = self.ctx.texture(
                (width, height), 
                4, 
                dtype='f1'
            )
            self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
            self.texture.swizzle = 'BGRA'
            self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])

    def render(self, surface):
        """Optimized render method"""
        # Update time with smaller increment for smoother animation
        self.time += 0.005
        
        # Convert surface to string only once
        texture_data = pygame.image.tostring(surface, 'RGBA', True)
        
        # Write texture data efficiently
        self.texture.write(texture_data)
        self.texture.use(0)
        
        # Update time uniform
        self.prog['time'].value = self.time
        
        # Render with minimal state changes
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def _optimized_fragment_shader(self):
        """Returns optimized GLSL fragment shader code"""
        return """
            #version 330
            uniform sampler2D tex;
            uniform float time;
            in vec2 uv;
            out vec4 fragColor;

            // Optimized random function
            float rand(vec2 co) {
                return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
            }

            // Simplified RGB shift
            vec3 rgbShift(vec2 uv) {
                const float amount = 0.001;
                return vec3(
                    texture(tex, uv + vec2(amount, 0.0)).r,
                    texture(tex, uv).g,
                    texture(tex, uv - vec2(amount, 0.0)).b
                );
            }

            // Optimized CRT warp
            vec2 crtWarp(vec2 uv) {
                vec2 cc = uv - 0.5;
                float dist = dot(cc, cc) * 0.2;
                return uv + cc * dist;
            }

            void main() {
                // Apply basic warping
                vec2 warpedUV = crtWarp(uv);
                
                // Simple horizontal distortion
                warpedUV.x += sin(warpedUV.y * 10.0 + time) * 0.001;
                
                // Check if UV is out of bounds
                if (warpedUV.x < 0.0 || warpedUV.x > 1.0 || 
                    warpedUV.y < 0.0 || warpedUV.y > 1.0) {
                    fragColor = vec4(0.0);
                    return;
                }
                
                // Get base color with RGB shift
                vec3 color = rgbShift(warpedUV);
                
                // Simplified scanline effect
                color *= 0.95 + 0.05 * sin(warpedUV.y * 600.0);
                
                // Simple vignette
                float vignette = 1.0 - dot(uv - 0.5, uv - 0.5) * 0.5;
                color *= vignette;
                
                // Reduced noise effect
                color += rand(uv + time) * 0.05;
                
                fragColor = vec4(color, 1.0);
            }
        """

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'vbo'):
            self.vbo.release()
        if hasattr(self, 'texture'):
            self.texture.release()
        if hasattr(self, 'fbo'):
            self.fbo.release()