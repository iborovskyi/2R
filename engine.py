#! /usr/bin/env python
# created by Ivan Borovskyi <imagination.fault@gmail.com>;
# licensed under BSD license;

class Engine(object):
    def __init__(self):
        # generic modules
        from random import randrange
        from copy import deepcopy
        self.randrange = randrange
        self.deepcopy = deepcopy
        from os import system
        self.system = system

        self.directions = {(-1,0): 'w', (1,0): 's', (0,-1): 'a', (0,1): 'd'}

    def level_creator(self):
        """
        creates random empty level map
        """
        self.level_map = []
        # max - 80 width; 20 height
        tile = {0: ' ', 1: '#'}
        cr_h = 0    # counter height
        while cr_h <= self.maxheight:
            level_string = []
            cr_w = 0    # counter width
            if cr_h == 0 or cr_h == self.maxheight:  # making up and bottom borders solid
                while cr_w <= self.maxwidth:
                    level_string.append('#')
                    cr_w += 1
            else:
                while cr_w <= self.maxwidth:
                    if cr_w == 0 or cr_w == self.maxwidth:   # making left and right borders solid
                        level_string.append('#')
                    else:
                        # making sure all paths are passable
                        if self.level_map[-1][cr_w] == ' ' and self.level_map[-1][cr_w + 1] == '#' or\
                            self.level_map[-1][cr_w] == ' ' and self.level_map[-1][cr_w - 1] == '#':
                            level_string.append(' ')
                        else:
                            level_string.append(tile[self.randrange(2)])
                            if cr_h == self.maxheight-1:
                                if self.level_map[-1][cr_w] == '#':
                                    level_string[-1] = ' '
                    cr_w += 1
            self.level_map.append(level_string)
            cr_h += 1


    def populator(self):
        """
        takes level_map (list of lists) from level_creator;
        returns self.active_map map (list of lists)
        """
        self.active_map = self.deepcopy(self.level_map)
        objs = ['^']
        for el in self.creatures.keys():
            objs.append(el)
        objs += self.loose_items
        for obj in objs:
            placed = False
            while placed != True:
                obj_h_pos = self.randrange(len(self.level_map))
                obj_w_pos = self.randrange(len(self.level_map[0]))
                if self.active_map[obj_h_pos][obj_w_pos] == ' ':
                    self.active_map[obj_h_pos][obj_w_pos] = obj
                    placed = True
                    if obj in self.creatures.keys():
                        self.creatures[obj][4] = [obj_h_pos, obj_w_pos]


    def player_sight_update(self):
        """
        updates player sight
        """
        player_h = self.creatures['@'][4][0]
        player_w = self.creatures['@'][4][1]
        drange = self.sight_range
        rangelen = range(-drange, drange+1)
        rangelen_h = []
        rangelen_w = []
        for i in rangelen:
            rangelen_h.append(i+player_h)
            rangelen_w.append(i+player_w)

        self.sight = []

        for row in range(self.maxheight+1):
            if row in rangelen_h:
                buf = []
                for tile in range(self.maxwidth+1):
                    if tile in rangelen_w:
                        buf.append(self.active_map[row][tile])
                    else:
                        buf.append(' ')
                self.sight.append(buf)
            else:
                self.sight.append([' ']*(self.maxwidth+1))

    def deal_damage(self, creature, target):
        """
        game without fighting is dull; fighting without dealing/taking damage is... well, it's not fighting in the first place
        takes two single characters as input
        """

        damage = self.randrange(self.creatures[creature][2][0],self.creatures[creature][2][1])
        for item in self.creatures[creature][6]:
            if self.items[item][1] == 'w':
                damage += self.randrange(self.items[item][2][0],self.items[item][2][1])

        resistance = self.randrange(self.creatures[target][3][0],self.creatures[target][3][1])
        for item in self.creatures[target][6]:
            if self.items[item][1] == 'a_b' or self.items[item][1] == 'a_h':
                resistance += self.randrange(self.items[item][2][0],self.items[item][2][1])

        if self.creatures[creature][1] > 0:
            if damage-resistance >= 0:
                self.creatures[target][1] -= (damage-resistance)
            self.upd_messages(self.creatures[creature][0] + ' attacks ' + self.creatures[target][0] + '! ')
            #self.upd_messages(self.creatures[creature][0] + ' attacks ' + self.creatures[target][0] + '! (' + str(self.creatures[target][1])+','+str(damage)+','+str(resistance)+')')  # for testing
            if self.creatures[target][1] <= 0:
                self.drop(target,'r')
                self.active_map[self.creatures[target][4][0]][self.creatures[target][4][1]] = self.creatures[target][5]
                if target != '@':
                    for item in self.creatures[target][6]:
                        self.drop(target, item)
                self.upd_messages(self.creatures[creature][0] + ' reduces ' + self.creatures[target][0] + ' to a pile of bones. ')

    def pick_up(self):
        '''
        pick up an item that is currently in character's tile buffer (self.creatures['@'][5]);
        '''
        if len(self.creatures['@'][6]) < 4:
            item = self.creatures['@'][5]

            cr_w = 0
            cr_a_b = 0
            cr_a_h = 0
            for el in self.creatures['@'][6]:
                if self.items[el][1] == 'w':
                    cr_w += 1
                elif self.items[el][1] == 'a_b':
                    cr_a_b += 1
                elif self.items[el][1] == 'a_h':
                    cr_a_h += 1
                else:
                    pass

            if item in self.items.keys():
                if self.items[item][1] == 'w':
                    if cr_w > 0:
                        self.upd_messages('You can not carry any more items of this type!')
                    else:
                        self.creatures['@'][6].append(item)
                        self.creatures['@'][5] = ' '
                        self.playEffect('item') # sound
                        self.upd_messages('You picked up ' + self.items[item][0] + '. ')
                elif self.items[item][1] == 'a_b':
                    if cr_a_b > 0:
                        self.upd_messages('You can not carry any more items of this type!')
                    else:
                        self.creatures['@'][6].append(item)
                        self.creatures['@'][5] = ' '
                        self.playEffect('item') # sound
                        self.upd_messages('You picked up ' + self.items[item][0] + '. ')
                elif self.items[item][1] == 'a_h':
                    if cr_a_h > 0:
                        self.upd_messages('You can not carry any more items of this type!')
                    else:
                        self.creatures['@'][6].append(item)
                        self.creatures['@'][5] = ' '
                        self.playEffect('item') # sound
                        self.upd_messages('You picked up ' + self.items[item][0] + '. ')
                else:
                    self.creatures['@'][6].append(item)
                    self.creatures['@'][5] = ' '
                    self.playEffect('item') # sound
                    self.upd_messages('You picked up ' + self.items[item][0] + '. ')
            else:
                self.upd_messages('Nothing to pick up here.')
        else:
            self.upd_messages('You can not carry any more items!')
                        
                    

    def drop(self, creature, item):
        '''
        takes creature (single char) and item (single char) as input;
        drops item from creature's inventory
        '''
        flag = False
        creature_coords = (self.creatures[creature][4][0],self.creatures[creature][4][1])
        deltas = [(0,0),(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)]

        for d in deltas:
            n_tile = (creature_coords[0]+d[0], creature_coords[1]+d[1]) # tile to drop item
            if d == (0,0) and self.creatures[creature][5] == ' ':
                self.creatures[creature][5] = item
                flag = True
                break
            if n_tile[0] in range(len(self.active_map)) and n_tile[1] in range(len(self.active_map[0])):
                if self.active_map[n_tile[0]][n_tile[1]] == ' ':
                    self.active_map[n_tile[0]][n_tile[1]] = item
                    flag = True
                    break

        if flag == True:
            buf = []
            for el in self.creatures[creature][6]:
                if el != item:
                    buf.append(el)
            item_ct =  len(self.creatures[creature][6]) - len(buf)
            while item_ct > 1:
                buf.append(item)
                item_ct -= 1
            self.creatures[creature][6] = buf
            self.playEffect('item')
            return(flag)
        else:
            return(flag)

    def drop_menu(self):
        '''
        player menu for dropping items
        '''
        if len(self.creatures['@'][6]) > 0:
            self.upd_messages('Which item would you like to drop? ("n" for cancel)')
            buf = ''
            for item in self.creatures['@'][6]:
                buf += item + ' - ' + self.items[item][0] + '; '
            self.upd_messages(buf)

            self.draw_screen()

            while 1:
                kbd_inp = ''
                event = self.pygame.event.poll()
                if event.type == self.pygame.KEYDOWN:
                    kbd_inp = (self.pygame.key.name(event.key))
                #kbd_inp = self.getch
                if kbd_inp == 'n':
                    self.upd_messages('Cancelled.')
                    break
                else:
                    if kbd_inp not in self.creatures['@'][6]:
                        pass
                    else:
                        flag = self.drop('@', kbd_inp)
                        if flag:
                            self.upd_messages('You drop ' + self.items[kbd_inp][0] + '. ')
                            break
                        else:
                            self.upd_messages('Nowhere to drop!')
                            break
                kbd_inp = ''
        else:
            self.upd_messages('Your inventory is empty!')
            kbd_inp = ''


    def show_inv(self):
        '''
        updates self.messages with string, describing inventory contents;
        '''
        self.upd_messages('Currently you carry: ')
        buf = ''
        for item in self.creatures['@'][6]:
            buf += item + ' - ' + self.items[item][0] + '; '
        self.upd_messages(buf)

    def check_health(self):
        '''
        updates self.messages with string, describing health of player character;
        '''
        if self.creatures['@'][1] > 79:
            self.upd_messages("Seems like you are feeling good.")
        elif self.creatures['@'][1] > 49:
            self.upd_messages("You are feeling normal.")
        elif self.creatures['@'][1] > 19:
            self.upd_messages("You are feeling weak. You should find a way to improve your health.")
        else:
            self.upd_messages("You are barely clinging to existance!")

    def mod_health(self):
        '''
        modifies character health, depending on yummy he/she/it consumed;
        '''
        edibles = []
        for item in self.creatures['@'][6]:
            if self.items[item][1] == 'p':
                edibles.append(item)
        if len(edibles) == 0:
            self.upd_messages("You have nothing edible in your inventory.")
            self.draw_screen()
        else:
            buf = ''
            for item in edibles:
                buf += item + ' - ' + self.items[item][0] + '; '
            self.upd_messages('Which of this would you like to eat? ("n" for cancel)')
            self.upd_messages(buf)
            self.draw_screen()
            while 1:
                kbd_inp = ''
                event = self.pygame.event.poll()
                if event.type == self.pygame.KEYDOWN:
                    kbd_inp = (self.pygame.key.name(event.key))
                #if kbd_inp != '':
                #    print(kbd_inp)
                if kbd_inp == 'n':
                    self.upd_messages('Cancelled.')
                    self.draw_screen()
                    break
                else:
                    if kbd_inp in edibles:
                        if kbd_inp != '':
                            if self.creatures['@'][1] == 100:
                                self.upd_messages('You are not hungry.')
                                self.draw_screen()
                                break
                            else:
                                if kbd_inp == 'r' and self.creatures['@'][1] > 50:
                                    self.upd_messages('You are not that hungry.')
                                    self.draw_screen()
                                    break
                                else:
                                    self.creatures['@'][1] += self.items[kbd_inp][2]
                                    if self.creatures['@'][1] > 100:
                                        self.creatures['@'][1] = 100
                                    buf = []
                                    eaten = False
                                    for item in self.creatures['@'][6]:
                                        if item == kbd_inp and eaten == False:
                                            eaten = True
                                        else:
                                            buf.append(item)
                                    self.creatures['@'][6] = buf
                                    self.upd_messages('You feel better now.')
                                    self.draw_screen()
                                    break
            

    def upd_messages(self, message):
        """
        updates list of messages;
        takes string of characters as input
        """
        if len(self.messages) == 6:
            self.messages = self.messages[1:]
        self.messages.append(message)



    def dummy_ai(self, creature):
        """
        uh... not sure, if it has to do something with "intelligence"...
        takes single character as input
        """
        creature_h = self.creatures[creature][4][0]
        creature_w = self.creatures[creature][4][1]
        player_h = self.creatures['@'][4][0]
        player_w = self.creatures['@'][4][1]

        if creature_h < player_h:
            delta_h = 1
        elif creature_h > player_h:
            delta_h = -1
        else:
            delta_h = 0

        if creature_w < player_w:
            delta_w = 1
        elif creature_w > player_w:
            delta_w = -1
        else:
            delta_w = 0

        move_deltas = [(delta_h,0), (0,delta_w)]
        path_tiles = [self.active_map[creature_h + delta_h][creature_w], self.active_map[creature_h][creature_w + delta_w]]

        if path_tiles[0] != '#' and path_tiles[1] == '#':
            self.upd_pos(creature, move_deltas[0])
        elif path_tiles[0] == '#' and path_tiles[1] != '#':
            self.upd_pos(creature, move_deltas[1])
        elif path_tiles[0] != '#' and path_tiles[1] != '#':
            if move_deltas[0] == (0,0):
                self.upd_pos(creature, move_deltas[1])
            elif move_deltas[1] == (0,0):
                self.upd_pos(creature, move_deltas[0])
            else:
                self.upd_pos(creature, move_deltas[self.randrange(2)])
        else:
            pass

    def upd_pos(self, creature, delta):
        """
        updates creature's position;
        takes creature sign and tuple of ints
        """
        try:
            direction = self.directions[delta]
        except KeyError:
            direction = self.creatures[creature][7]

        if self.creatures[creature][1] > 0:
            creature_h = self.creatures[creature][4][0]
            creature_w = self.creatures[creature][4][1]
            if creature == '@' and self.active_map[creature_h+delta[0]][creature_w+delta[1]] == '^':
                self.flag = 'win'
            elif self.active_map[creature_h+delta[0]][creature_w+delta[1]] not in '#^':
                if 0 <= creature_h+delta[0] <= len(self.active_map)-1 and 0 <= creature_w+delta[1] <= len(self.active_map[0])-1:
                    if self.active_map[creature_h+delta[0]][creature_w+delta[1]] != '#':
                        if self.active_map[creature_h+delta[0]][creature_w+delta[1]] in self.creatures.keys() and \
                               creature != self.active_map[creature_h+delta[0]][creature_w+delta[1]]:

                           # attack animations
                           self.creatures[creature][7] = direction
                           self.tileLogic(creature, m_type = 'attack')

                           self.deal_damage(creature, self.active_map[creature_h+delta[0]][creature_w+delta[1]])
                           if creature == '@':
                                buf = []
                                for string in self.sight:
                                    buf += string
                                for el in self.creatures.keys():
                                    if el in buf and el != '@':
                                        self.dummy_ai(el)
                        else:
                            # walk animations
                            self.creatures[creature][7] = direction
                            self.tileLogic(creature, delta, m_type = 'walk')

                            self.active_map[creature_h][creature_w] = self.creatures[creature][5]
                            self.creatures[creature][5] = self.active_map[creature_h+delta[0]][creature_w+delta[1]]
                            self.active_map[creature_h+delta[0]][creature_w+delta[1]] = creature
                            self.creatures[creature][4] = [creature_h+delta[0],creature_w+delta[1]]
                            if creature == '@':
                                buf = []
                                for string in self.sight:
                                    buf += string
                                for el in self.creatures.keys():
                                    if el in buf and el != '@':
                                        self.dummy_ai(el)
                self.player_sight_update()

    def draw_screen(self):
        """
        redraws screen
        """
        #self.system('clear')

        ###for testing
        ##for string in self.active_map:
        ##    buf = ''
        ##    for char in string:
        ##        if char in self.creatures.keys():
        ##            buf += self.creatures[char][9]
        ##        else:
        ##            buf += char
        ##    print(buf)
        ##print('\n')

        #for string in self.sight:
        #    buf = ''
        #    for char in string:
        #        if char in self.creatures.keys():
        #            buf += self.creatures[char][9]
        #        else:
        #            buf += char
        #    print(buf)
        #for string in self.messages:
        #    print(string)

        # pygame screen redraw
        self.DISPLAYSURF.fill(((0,0,0)))     # filling black
        self.tileLogic()
        self.DISPLAYSURF.blit(self.gamelog_bg, (0, 570))   # Draw text bg
        self.drawText(self.messages, 570)
        self.reDraw()


    def readFile(self, file_path):
        '''
        Read file contents
        '''
        txt = []
        f = open(file_path, 'r')
        for l in f:
            txt.append(l[:-1])

        return(txt)
