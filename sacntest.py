import pygame, sys, os
from pygame.locals import *
import sacn
import time

# global variables
ipaddress = "192.168.1.146"
universecount = 16
screen_width = 48
screen_height = 56
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)


def sendscreen(screen, sender):
    a = ()
    for x in range(9):
       color = screen.get_at((x, 0))[:3]
       a = (a + color)
    sender[1].dmx_data = a

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
        # print(column)
        # print(x, " ", y)
    # for i in range(0, len(all), 170):
    for i in range(universecount):
        sender[i+1].dmx_data = all[i*510:i*510+510]
        # print(i, " ", i*170, " ", i * 170 + 170)
    # print(all)

    sender.flush()
    sender.manual_flush = False # keep maunal flush off as long as possible, because if it is on, the automatic


def drawscreen(screen, pygame, colors, y):
    h = screen_height / 4
    w = screen_width / 4

    screen.fill(BLACK)

    pygame.draw.rect(screen, colors[3], (0, 0, screen_width, screen_height))
    for x in range(4):
		    # pygame.draw.rect(screen, colors[x], (0, h*x+y, screen_width, h*x+h+y))
		    pygame.draw.rect(screen, colors[x], (w*x+y, 0, w*x+w+y, screen_height))

    pygame.draw.rect(screen, BLACK, (screen_width + 1, 0, 200, screen_height))
    y += 1
    # if y == h:
    if y == w:
      y = 0
      colors = (colors[3], colors[0], colors[1], colors[2])

    return colors, y

def main():
    # set up sacn
    sender = sacn.sACNsender()  # provide an IP-Address to bind to if you are using Windows and want to use multicast
    sender.start()  # start the sending thread

    # sender[1].multicast = True  # set multicast to Tru
    for i in range(universecount):
        sender.activate_output(i+1)  # start sending out data in the 1st universe
        sender[i+1].destination = ipaddress  # or provide unicast information.
    # Keep in mind that if multicast is on, unicast is not used

    #set up the fpx
    pygame.init()
    FPS = 5 #frames per second setting
    fpsClock = pygame.time.Clock()

    #set up the window
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (20,400)
    screen = pygame.display.set_mode([screen_width, screen_height])
    pygame.display.set_caption('animation')

    colors = (RED, GREEN, BLUE, WHITE, 0)
    y = 0

    # loop till we see the window closed
    while True: # the main game loop
        colors, y = drawscreen(screen, pygame, colors, y)

        for event in pygame.event.get():
            if event.type == QUIT:
                sender.stop()
                pygame.quit()
                sys.exit()
        # screen.get_at((x, y))[:3]
        # print(screen.get_at((0, 0))[:3])

        pygame.display.update()
        sendscreen2(screen, sender)
        fpsClock.tick(FPS)


if __name__ == "__main__":
    main()
