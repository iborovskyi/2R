#!/usr/bin/env python
# created by Ivan Borovskyi <imagination.fault@gmail.com>;
# licensed under BSD license;

class initSound(object):
    def __init__(self):
        from os import listdir
        self.listdir = listdir
        # Sounds
        #themes
        self.themes_dir = 'sounds/themes/'
        # themes set in settings.conf
        self.current_theme = None
        #effects
        self.efcts_dir = 'sounds/effects/'
        self.efcts = {}
        self.setSoundEffects()
        #volume - set in settings.conf

    def setSoundEffects(self):
        '''
        sets effects
        '''
        self.efcts['hits'] = self.listdir(self.efcts_dir+'hits/')
        self.efcts['steps'] = self.listdir(self.efcts_dir+'steps/')
        self.efcts['item'] = self.listdir(self.efcts_dir+'item/')

    def playEffect(self, efct_grp):
        '''
        Play effect sound
        '''
        efct_name = self.efcts_dir + efct_grp + '/' + self.efcts[efct_grp][self.randrange(len(self.efcts[efct_grp]))]
        effect = self.pygame.mixer.Sound(efct_name)
        #self.pygame.mixer.Sound.set_volume(self.effectVol)
        effect.set_volume(self.effectVol)
        effect.play()

    def playTheme(self, path):
        '''
        Play sound
        '''
        self.pygame.mixer.music.load(path)
        self.pygame.mixer.music.set_volume(self.musicVol)
        self.pygame.mixer.music.play(-1)

        self.current_theme = self.pygame.mixer.music

    def updVol(self, vol, delta, sound, vol_name):
        '''
        Update music volume
        '''
        vol += delta

        if vol < 0:
            vol = 0.0
        elif vol > 1:
            vol = 1.0

        if vol_name == 'm':
            self.musicVol = vol
        elif vol_name == 'e':
            self.effectVol = vol
        sound.set_volume(self.musicVol)

    def stopTheme(self):
        '''
        Stop playing sound
        '''
        self.pygame.mixer.music.stop()
