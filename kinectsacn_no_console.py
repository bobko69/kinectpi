import pygame, sys, os
from pygame.locals import *
import sacn
import time
import numpy as np
from freenect import sync_get_depth as get_depth

# global variables
ipaddress = "4.3.2.1"
universecount = 16
screen_width = 48
screen_height = 56

#crontab -e @reboot python3 /home/bob/kinectsacn_no_console.py 

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
            a = np.array([0, 0, 0], dtype=np.uint8)
        elif pval == 1:
            a = np.array([255 - lb, lb, 0], dtype=np.uint8)
        elif pval == 2:
            a = np.array([0, 255 - lb, lb], dtype=np.uint8)
        elif pval == 3:
            a = np.array([lb, 0, 255 -  lb], dtype=np.uint8)
        elif pval == 4:
            a = np.array([0, 0, 0], dtype=np.uint8)
        elif pval == 5:
            a = np.array([0, 0, 0], dtype=np.uint8)
        else:
            a = np.array([0, 0, 0], dtype=np.uint8)

        _gamma[i] = a
    return _gamma


gamma = make_gamma()


def sendscreen2(screen, sender):
    all = ()
    sender.manual_flush = True # turning off the automatic sending of packets
    for x in range(screen_width):
        column = ()
        for y in range(screen_height):
            pixel = screen.get_at((x, y))[:3]
            if (x % 2) == 0:
                column = (pixel + column)
            else:
                column = (column + pixel)
        all = (all + column)
    for i in range(universecount):
        sender[i+1].dmx_data = all[i*510:i*510+510]

    sender.flush()
    sender.manual_flush = False # keep maunal flush off as long as possible, because if it is on, the automatic



def main():
    # set up sacn
    sender = sacn.sACNsender()  # provide an IP-Address to bind to if you are using Windows and want to use multicast
    sender.start()  # start the sending thread
    # sender[1].multicast = True  # set multicast to Tru
    for i in range(universecount):
        sender.activate_output(i+1)  # start sending out data in the 1st universe
        sender[i+1].destination = ipaddress  # or provide unicast information.
        #sender[i+1].multicast = True  # set multicast to True
        # Keep in mind that if multicast is on, unicast is not used

    #set up the fpx
    pygame.init()
    FPS = 5 #frames per second setting
    fpsClock = pygame.time.Clock()
    disp_size = (640, 480)

    #set up the window
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (20,20)
#    screen = pygame.display.set_mode(disp_size)
    screen = pygame.Surface(disp_size)
#    pygame.display.set_caption('animation')


    # loop till we see the window closed
    while True: # the main game loop
#        for event in pygame.event.get():
#            if event.type == QUIT:
#                sender.stop()
#                pygame.quit()
#                sys.exit()

        depth = np.rot90(get_depth()[0]) # get the depth readinngs from the camera
        pixels = gamma[depth] # the colour pixels are the depth readings overlayed onto the gamma table
        temp_surface = pygame.Surface(disp_size)
        pygame.surfarray.blit_array(temp_surface, pixels)
        pygame.transform.scale(temp_surface, disp_size, screen)
        cropped = pygame.Surface((630, 480))
        cropped.blit(temp_surface,(0,0), (10,0,640,480))
        led_surface = pygame.Surface((48,56))
        led_surface = pygame.transform.scale(cropped, (48,56))
#        screen.blit(led_surface, (0,0))
        # pygame.display.flip()

        sendscreen2(led_surface, sender)
        fpsClock.tick(FPS)


if __name__ == "__main__":
    main()
