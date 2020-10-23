#!/usr/bin/env python
# created by Ivan Borovskyi <imagination.fault@gmail.com>;
# licensed under BSD license;

from engine import Engine
from DG import initScreen
from sound_caster import initSound

class Game(initScreen, initSound, Engine):
    def __init__(self):

        # game state flag
        self.flag = 'alive'

        # importing configuration
        self.loadConf('game_config.conf')
        self.loadConf('settings.conf')


        #initializing engine
        Engine.__init__(self)
        self.level_creator()
        self.populator()

        # initializing screen
        initScreen.__init__(self)
        self.loadImages()

        # initializing sound
        initSound.__init__(self)

        self.sight = []     # tiles, seen to player; list of lists; changeable
        self.messages = []

    def loadConf(self, conf_file):
        '''
        Load configuration from tex files
        '''
        f = open(conf_file,'r')
        multiline = ''

        for l in f.readlines():
            #try:
            #    print(l[-2])
            #except:
            #    pass
            if l[0] != '#' and len(l) > 1:
                if l[-2] != '\\':
                    if len(multiline) == 0:
                        exec(l)
                        #print(l)
                    else:
                        multiline += l
                        exec(multiline)
                        #print(multiline)
                        multiline = ''
                else:
                    multiline += l[:-2]
        f.close()


    def credits(self, d_y, txt):
        # Credits
        kbd_inp = ''
        while d_y > -(len(txt)*40) and kbd_inp =='':
            event = self.pygame.event.poll()
            if event.type == self.pygame.KEYDOWN:
                kbd_inp = (self.pygame.key.name(event.key))
            self.DISPLAYSURF.blit(self.bg, (0, 0))   # Draw text bg
            self.drawText(txt, d_y)
            self.reDraw()
            d_y -= 2

    def runGame(self):
        """
        responsible for interactions with user
        """
        self.fullscMsg(self.readFile('txts/intro.txt'))

        self.upd_messages("For help press 'h'.")
        self.draw_screen()
        self.playTheme(self.themes_dir+self.main)

        while self.flag == 'alive':
            self.reDraw()
            if self.creatures['@'][1] <= 0:
                self.flag = 'dead'
                break
            
            kbd_inp = ''
            event = self.pygame.event.poll()
            if event.type == self.pygame.KEYDOWN:
                kbd_inp = (self.pygame.key.name(event.key))

            input_dict = {'w': (-1,0), 'a': (0,-1), 's': (1,0), 'd':(0,1)}
            musicVol_dict = {',': -0.1, '.': 0.1}
            effectVol_dict = {'[': -0.1, ']': 0.1}


            if kbd_inp in input_dict.keys():
                self.upd_pos('@',input_dict[kbd_inp])
                self.draw_screen()
            else:
                if kbd_inp in [ 'i', 'p', 'o', 'c' ]:
                    if kbd_inp == 'i':
                        self.show_inv()
                    elif kbd_inp == 'p':
                        self.pick_up()
                    elif kbd_inp == 'o':
                        self.drop_menu()
                        self.player_sight_update()
                    elif kbd_inp == 'c':
                        self.check_health()
                    self.draw_screen()
                else:
                    if kbd_inp == 'e':
                        self.mod_health()
                    elif kbd_inp in musicVol_dict.keys():
                        self.updVol(self.musicVol,musicVol_dict[kbd_inp],self.current_theme,'m')
                    elif kbd_inp in effectVol_dict.keys():
                        self.updVol(self.effectVol,effectVol_dict[kbd_inp],self.current_theme,'e')
                    elif kbd_inp == 'q':
                        break
                    elif kbd_inp == 'h':
                        self.fullscMsg(self.readFile('txts/help.txt'))
                        self.draw_screen()
                    elif kbd_inp == ';':
                        self.credits(1224, self.readFile('txts/credits.txt'))
                        self.draw_screen()
                    else:
                        pass
        if self.flag == 'dead':

            self.stopTheme()
            self.playTheme(self.themes_dir+self.defeat)

            if 'h' in self.creatures['@'][6] and 'P' in self.creatures['@'][6] and 's' in self.creatures['@'][6]:
                txt = self.readFile('txts/defeat_alt.txt')
            else:
                txt = self.readFile('txts/defeat.txt')

            self.fullscMsg(txt)
            self.reDraw()
        if self.flag == 'win':

            self.stopTheme()
            self.playTheme(self.themes_dir+self.outro)

            self.fullscMsg(self.readFile('txts/outro.txt'))
            self.reDraw()

        if self.flag == 'win':
            achievements = []
            if 'h' in self.creatures['@'][6] and 'p' in self.creatures['@'][6] and 's' in self.creatures['@'][6] and self.creatures['B'][1] <= 0:
                achievements += (self.readFile('txts/achievement_viking.txt'))
            Gandhi = True
            butcher = True
            for creature in self.creatures:
                if self.creatures[creature][1] <= 0:
                    Gandhi = False
                if self.creatures[creature][1] > 0 and creature != '@':
                    butcher = False
            if Gandhi == True:
                achievements += (self.readFile('txts/achievement_gandhi.txt'))
            if butcher == True:
                achievements += (self.readFile('txts/achievement_butcher.txt'))
            gold = 0
            for item in self.creatures['@'][6]:
                if item == '=':
                    gold += 1
            if gold == 4:
                achievements += (self.readFile('txts/achievement_greed.txt'))

            if len(achievements) > 0:
                txt = ["Congratulations! Your achievements for this run:", " "] + achievements
                self.fullscMsg(txt)
                self.reDraw()

            self.credits(1224, self.readFile('txts/credits.txt'))
            self.fullscMsg(['Thanks for playing!'])
            self.reDraw()

R = Game()
R.runGame()
