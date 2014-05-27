import pygame, threading, time, logging

class NoiseMaker(threading.Thread):
    """
    Allows Doorbell to do noise-playing operations in a parallel thread.
    """

    def __init__(self, channel):
        """
        Set up a default stereo sound player with a low-latency small buffer.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        pygame.mixer.init(channels=2, buffer=512)
        self.channel = pygame.mixer.Channel(channel)
        self.delay = 0
        self.playing = False
        self.logging = logging.getLogger(self.__class__.__name__)

    def setsoundfile(self, soundfile):
        """
        (Re)set the soundfile that this NoiseMaker is supposed to play when asked.
        """
        self.sound = pygame.mixer.Sound(soundfile)

    def setlocation(self, location):
        """
        Determines where to play the sound. We support two audio channels, using
        L for outside, R for inside, and full stereo for both.
        """
        self.location = location

    def setdelay(self, delay):
        """
        Sets a delay, in seconds, before playback of our sound.
        """
        self.delay = delay

    def run(self):
        """
        If we're supposed to play a sound, play it in the configured location(s).
        """
        while self.running:
            if self.playing:
                if self.delay > 0:
                    time.sleep(self.delay)
                self.channel.play(self.sound)
                if self.location == "inside":
                    self.channel.set_volume(1,0) # play in the L channel
                elif self.location == "outside":
                    self.channel.set_volume(0,1) # play in the R channel
                elif self.location == "both":
                    self.channel.set_volume(1,1) # play in both chanels
                else:
                    self.channel.set_volume(1,1) # play in both chanels
                    self.logging.warn("(" + self.__class__.__name__ + ") unsupported sound location: '" + self.location + "'; defaulting to 'both'")
                self.playing = False
            time.sleep(0.01)

    def stop(self):
        self.running = False

    def play(self):
        self.playing = True
