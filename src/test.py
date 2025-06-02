import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from pyvidplayer2 import Video

win = pygame.display.set_mode((1024, 572), DOUBLEBUF)
vid = Video("assets/video/cutscenes/prelude.mp4")
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            exit()

    pygame.time.wait(16)
    vid.draw(win,(0,0), force_draw=False)
    pygame.display.flip()