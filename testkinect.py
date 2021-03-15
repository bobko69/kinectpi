import pygame
import numpy as np
import sys
from freenect import sync_get_depth as get_depth


def make_gamma():
    """
    Create a gamma table
    """
    num_pix = 2048 # there's 2048 different possible depth values
    npf = float(num_pix)
    _gamma = np.empty((num_pix, 3), dtype=np.uint16)
    for i in range(num_pix):
        v = i / npf
        v = pow(v, 3) * 6
        pval = int(v * 6 * 256)
        lb = pval & 0xff
        pval >>= 8
        if pval == 0:
#            a = np.array([255, 255 - lb, 255 - lb], dtype=np.uint8)
            a = np.array([0, 0, 0], dtype=np.uint8)
        elif pval == 1:
            a = np.array([255 - lb, lb, 0], dtype=np.uint8)
        elif pval == 2:
            a = np.array([0, 255 - lb, lb], dtype=np.uint8)
        elif pval == 3:
            a = np.array([lb, 0, 255 -  lb], dtype=np.uint8)
        elif pval == 4:
#            a = np.array([0, 255 - lb, 255], dtype=np.uint8)
            a = np.array([0, 0, 0], dtype=np.uint8)
        elif pval == 5:
#            a = np.array([0, 0, 255 - lb], dtype=np.uint8)
            a = np.array([0, 0, 0], dtype=np.uint8)
        else:
            a = np.array([0, 0, 0], dtype=np.uint8)

        _gamma[i] = a
    return _gamma


gamma = make_gamma()


if __name__ == "__main__":
    fpsClock = pygame.time.Clock()
    FPS = 5 # kinect only outputs 30 fps
    disp_size = (640, 480)
    pygame.init()
    screen = pygame.display.set_mode(disp_size)
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit()
        fps_text = "FPS: {0:.2f}".format(fpsClock.get_fps())
        # draw the pixels

        depth = np.rot90(get_depth()[0]) # get the depth readinngs from the camera
        pixels = gamma[depth] # the colour pixels are the depth readings overlayed onto the gamma table
        temp_surface = pygame.Surface(disp_size)
        pygame.surfarray.blit_array(temp_surface, pixels)
        cropped = pygame.Surface((630, 480))
        cropped.blit(temp_surface,(0,0), (10,0,640,480))
        pygame.transform.scale(temp_surface, disp_size, screen)
        temp_screen = pygame.Surface((48,56))
        temp_screen = pygame.transform.scale(cropped, (48,56))
        screen.blit(temp_screen, (0,0))
        pygame.display.flip()
        fpsClock.tick(FPS)
