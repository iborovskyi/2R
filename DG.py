#!/usr/bin/env python
# created by Ivan Borovskyi <imagination.fault@gmail.com>;
# licensed under BSD license;

class initScreen(object):
    def __init__(self):
        from time import sleep
        self.sleep = sleep
        import pygame
        self.pygame = pygame
        self.pygame.init()
        self.DISPLAYSURF = self.pygame.display.set_mode((1024, 768), self.pygame.DOUBLEBUF)    #set the display mode, window title and FPS clock
        #self.DISPLAYSURF = self.pygame.display.set_mode((1024, 768), self.pygame.HWACCEL|self.pygame.DOUBLEBUF)    #set the display mode, window title and FPS clock

        # User configuration
        # now loaded in __init__ of run

        self.pygame.display.set_caption('The Revenant')
        self.tileWidth = 128  #holds the tile width and height
        self.tileHeight = 128
        self.font = self.pygame.font.Font('fonts/'+self.font, self.font_size)

        icon = self.pygame.image.load(self.tiles_dir+"/misc/icon.png").convert_alpha()
        self.pygame.display.set_icon(icon)  # window icon

        # misc variables
        self.creature_template = { 'walk': {'w': [], 'a': [], 's': [], 'd': [] }, 'attack': {'w': [], 'a': [], 's': [], 'd': [] } }


    def reDraw(self):
        '''
        Redraw screen (applies all changes made by tileLogic, drawText, etc.)
        '''
        FPSCLOCK = self.pygame.time.Clock()
        self.pygame.display.flip()
        FPSCLOCK.tick(self.fps)


    def drawText(self, txt, start_delta):
        '''
        Draw text
        start_delta - number of pixels from the bottom
        '''
        txt_start_y = 768 + start_delta
        for string in txt:
            self.text = self.font.render(string, True, (0,0,0))
            delta = self.text.get_height() + 20
            self.DISPLAYSURF.blit(self.text, ((1024 - self.text.get_width()) // 2, \
                    ((txt_start_y - ((delta*len(txt))/2) ) // 2)))    # Draw text
            txt_start_y += delta


    def loadImages(self):
        '''
        Glues all image loading together
        '''
        # None iterable loads
        print('LOADING MISC')
        self.bg = self.pygame.image.load(self.tiles_dir+"/misc/scroll_fullscreen.png").convert_alpha()
        self.gamelog_bg = self.pygame.image.load(self.tiles_dir+"/misc/scroll_gamelog.png").convert_alpha()
        self.floor = []
        self.stairs = self.pygame.image.load(self.tiles_dir+"/misc/staircase.png").convert_alpha()
        self.blank = self.pygame.image.load(self.tiles_dir+"/misc/blank.png").convert_alpha()  #load images
        self.black = self.pygame.image.load(self.tiles_dir+"/misc/black.png").convert_alpha()  #load images
        self.fog = self.pygame.image.load(self.tiles_dir+"/misc/fog_of_war1.png").convert_alpha()  #load images
        self.default = self.pygame.image.load(self.tiles_dir+"/misc/default.png").convert_alpha()  #load images

        # Dict is populated by other load functions; tileLogic will shit itself if it does not find something here
        # (Not literally - just load an ugly default)
        # Maybe I should remove this totally? Later.
        self.tiles = { '1': self.blank, ' ': self.floor, '^': self.stairs }


        # Load creatures
        print('LOADING CREATURES')
        for c in self.creatures.keys():
            if c[0] in self.tiles.keys():
                self.tiles[c] = self.tiles[c[0]]
            else:
                self.loadAnimated('/creatures_', c, self.creatures, 8, c)

        # Load items
        print('LOADING ITEMS')
        for i in self.items:
            self.tiles[i] = self.pygame.image.load(self.tiles_dir+'/drop/'+self.items[i][3]+'.png').convert_alpha()
            if self.items[i][1] in ['w', 'a_b']:
                if self.items[i][4] not in self.tiles.keys():
                    self.loadAnimated('/equips_', i, self.items, 4, self.items[i][4])

        print('LOADING WALLS')
        self.loadWalls()
        print('LOADING FLOOR')
        self.loadFloor()
        print('ASSIGNING UNIQUE TEXTURES')
        self.uniTex()

        


    def loadAnimated(self, path_part, tKey, tList, posNum, entryName):
        '''
        Load animation
        a bit ugly
        path_part - subdirectory name part
        tKey - key of the dict textures should be loaded to
        tList - list from where name part is taken
        entryName - texture name part
        '''
        # Loading creatures

        self.tiles[entryName] = self.deepcopy(self.creature_template)
        for k in 'wasd':
            for m_type in [('walk','_'), ('attack', '_a_')]:    # movement type
                cr = 0
                while 1:
                    try:
                        print(self.tiles_dir+path_part+m_type[0]+'/'+tList[tKey][posNum]+m_type[1]+k+str(cr)+'.png')
                        self.tiles[entryName][m_type[0]][k].append(self.pygame.image.load(self.tiles_dir+path_part+m_type[0]+'/'+\
                                tList[tKey][posNum]+m_type[1]+k+str(cr)+'.png').convert_alpha())
                    except:
                        break
                    cr += 1

    def loadFloor(self):
        '''
        Load floor textures
        '''
        cr = 0
        while 1:
            try:
                print(self.tiles_dir+'/floor/floor'+str(cr)+'.png')
                self.tiles[' '].append(self.pygame.image.load(self.tiles_dir+'/floor/floor'+str(cr)+'.png').convert_alpha())
            except:
                break
            cr += 1


    def loadWalls(self):
        '''
        Load walls textures
        '''
        # First list of the value ([' # ### # ']) contains 3x3 map parts in string format
        self.walls = {0: [[' # ### # '],[]],
                1: [['###### # ', '   ### # ', '   ##### ', '   ### ##'], []],
                2: [['### ## # ', ' ## ## # '], []],
                3: [[' # ######'],[]],
                4: [['#####  # ', '## ##  # '],[]],
                5: [['## ######', '### ##  #', '### ##   ', ' ## ##   ', ' ## ##  #'], []],
                6: [['###### ##', '   ##  # ', '   ## ## ', '   ## ###'], []],
                7: [['######## ', '    ## ##' , '    #####', '    ## # '], []],
                8: [['#####    ', '##### #  ', '## ## #  ', '## ##    ', ' ########'], []],
                9: [['####### #', '#######  ', '######  #', '######   ', '   ####  ', '   ###  #', '   #### #', '   ######', '   ###   ',
                    '#  ######', '  #######', '# #######'], []],
                10: [['##### ## ', '## ## ## ', '## ## ###', '### ## ##', '### #  # ', '##  #  # ', ' ## #  # ', ' #  #  # ',
                    ' ## ## ##', ' ## #####'], []],
                11: [['    ##  #', '    ##   '], []],
                12: [[ '   ##    ', '   ## #  '], []],
                13: [['### #    ', '##  #    ', ' ## #    ', ' #  #    '], []],
                14: [['    #  # ', '    # ###'], []],
                15: [['    #    '], []]}

        self.walls_tp = {0: [[' # ### # '], []],
                1: [['   ### # ', '   ##### ', '   ### ##'], []],
                2: [['### ## # ', ' ## ## # '], []],
                3: [[' # ######'], []],
                4: [[], []],
                5: [['### ##  #', '### ##   ', ' ## ##   ', ' ## ##  #'], []],
                6: [['   ##  # ', '   ## ## ', '   ## ###'], []],
                7: [['    ## ##', '    #####', '    ## # '], []],
                8: [[' ########'], []],
                9: [['   ####  ', '   ###  #', '   #### #', '   ######', '   ###   ', '#  ######', '  #######',
                    '# #######'], []],
                10: [['### ## ##', '### #  # ', '##  #  # ', ' ## #  # ', ' #  #  # ', ' ## ## ##',
                    ' ## #####'], []],
                11: [['    ##  #', '    ##   '], []],
                12: [[ '   ##    ', '   ## #  '], []],
                13: [['### #    ', '##  #    ', ' ## #    ', ' #  #    '], []],
                14: [['    #  # ', '    # ###'], []],
                15: [['    #    '], []]}

        for K in self.walls.keys():
            cr = 0
            while 1:
                try:
                    print(self.tiles_dir+'/walls/wall_'+str(K)+'_'+str(cr)+'.png')
                    self.walls[K][1].append(self.pygame.image.load(self.tiles_dir+'/walls/wall_'+str(K)+\
                            '_'+str(cr)+'.png').convert_alpha())
                except:
                    break
                cr += 1

        for K in self.walls_tp.keys():
            cr = 0
            while 1:
                try:
                    print(self.tiles_dir+'/walls/wall_tp_'+str(K)+'_'+str(cr)+'.png')
                    self.walls_tp[K][1].append(self.pygame.image.load(self.tiles_dir+'/walls/wall_tp_'+str(K)+\
                            '_'+str(cr)+'.png').convert_alpha())
                except:
                    break
                cr += 1


    def uniTex(self):
        '''
        Create a list with corresponding textures for each tile
        '''
        self.level_textures = []
        debug_missing = []
        for row in range(len(self.level_map)):
            self.level_textures.append([])
            for tile in range(len(self.level_map[0])):
                    if self.level_map[row][tile] == ' ':        # here unique floor textures are assigned
                        if self.randrange(10) > 4:
                            self.level_textures[row].append(self.randrange(len(self.tiles[' '])))
                        else:
                            self.level_textures[row].append(0)
                    # else we should determine what type of tile should it be...
                    else:
                        surrounding_tiles = ''  # surrounding the  current one
                        drange = 1
                        for h in range(-drange, drange+1):
                            if h + row in range(self.maxheight+1):
                                for w in range(-drange, drange+1):
                                    if w + tile in range(self.maxwidth+1):
                                        surrounding_tiles += self.level_map[h + row][w + tile]
                                    else:
                                        surrounding_tiles += '#'
                            else:
                                surrounding_tiles += '#'*((drange*2)+1)


                        # ...and chooses the texture
                        if ' ' not in surrounding_tiles:
                            self.level_textures[row].append(None)
                        else:
                            xy = surrounding_tiles[1]+surrounding_tiles[3]+surrounding_tiles[5]+surrounding_tiles[7]
                            cr = 0
                            for K in self.walls.keys():
                                if surrounding_tiles in self.walls[K][0]:
                                    if (row != len(self.level_map)-1 and tile != len(self.level_map[0])-1) and \
                                            (surrounding_tiles[5] == ' ' or surrounding_tiles[7] == ' ') and \
                                            self.randrange(10) > 5:
                                        self.level_textures[row].append((K,self.randrange(len(self.walls[K][1]))))
                                    else:
                                        self.level_textures[row].append((K,0))
                                    break
                                cr += 1
                                if cr == len(self.walls):
                                    if surrounding_tiles not in debug_missing:
                                        debug_missing.append(surrounding_tiles)
        print('MISSING WALLS: ' + str(len(debug_missing)))
        for t in debug_missing:
            print('~'*8)
            print"'"+t+"'"
            print(t[:3]+'\n'+t[3:6]+'\n'+t[6:])

        # Notifying the game that walls are loaded!
        self.tiles['#'] = True



    def isTp(self, row, tile):
        '''
        Determines if tile should be transparent
        '''
        self.player_sight_update()
        for h in range(-1, 2):
            if h + row in range(self.maxheight+1):
                for w in range(-1, 2):
                    if w + tile in range(self.maxwidth+1):
                        #if (h,w) in [(-1,-1),(0,-1)] and self.sight[h + row][w + tile] not in '# ':
                        if (h,w) == (-1,-1) and self.sight[h + row][w + tile] not in '# ':
                            return(True)
        return(False)





    def updTile(self, cTile, cRow, tImage, delta = (0,0)):
        '''
        Update tile texture
        '''
        c_w = self.creatures['@'][4][1]
        c_h = self.creatures['@'][4][0]
        cartx = cTile * self.tileWidth    #x is the index of the currentTile * the tile width
        carty = cRow * self.tileHeight     #y is the index of the currentRow * the tile height

        x = 450 + ((cartx - carty + delta[1]) / 2)
        y = -128 + ((cartx + carty + delta[0])/4)
        self.pygame.Color(0,0,0,0)

        self.DISPLAYSURF.blit(tImage, (x, y)) #display the actual tile


    def updDsight(self):
        '''
        Function to help draw sight in graph
        Range for draw sight is sight range + 2 tiles to get it smooth
        '''
        self.dsight = []
        self.dsight_coords = []
        player_h = self.creatures['@'][4][0]
        player_w = self.creatures['@'][4][1]
        drange = self.sight_range+2
        for h in range(-drange, drange+1):
            if h + player_h in range(self.maxheight+1):
                buf = []
                buf_coords = []
                for w in range(-drange, drange+1):
                    if w + player_w in range(self.maxwidth+1):
                        buf.append(self.active_map[h + player_h][w + player_w])
                        buf_coords.append((h + player_h, w + player_w))
                    else:
                        buf.append('1')
                        buf_coords.append(None)
                self.dsight.append(buf)
                self.dsight_coords.append(buf_coords)
            else:
                self.dsight.append(['1']*((drange*2)+1))
                self.dsight_coords.append([None]*((drange*2)+1))



    def tileLogic(self, moved = None, delta = (0,0), cr_r = 0, starting_tile = None, m_type = None):
        '''
        Monster function which determins which tile should be passed to updTile
        It should be made simplier somehow...
        moved - a tile that moved
        delta - coordinate delta for moved tile
        cr_r - counter of recursion; not passed from any other function but tileLogic itself
        starting_tile - coordinates of starting tile (passed by tileLogic itself)
        m_type - movement type (walk, attack)
        '''



        def drawPlayer(isReverse, m_type, moved, mdelta, cr_rec = cr_r):
            # Subfunction. Ugly(

            # Equips
            armor = []
            weapons = []

            for i in self.creatures['@'][6]:
                if self.items[i][1] == 'a_b':
                    armor.append(self.items[i][4])
            if len(armor) == 0:
                armor = ['@']
            for i in self.creatures['@'][6]:
                if self.items[i][1] == 'w':
                    weapons.append(self.items[i][4])

            for l in (armor, weapons):
                for i in l:
                    tileImage = self.tiles[i][m_type][self.creatures[moved][7]][cr_rec/2]
                    if isReverse == True:
                        self.updTile(currentTile-delta[1], currentRow-delta[0], tileImage, mdelta)
                    else:
                        self.updTile(currentTile, currentRow, tileImage, mdelta)

        def getFloorTex():
            # Another subfunction. Getting uglier..
            coords = self.dsight_coords[currentRow][currentTile]
            tile_tex = self.level_textures[coords[0]][coords[1]]
            return(self.tiles[' '][self.level_textures[coords[0]][coords[1]]])

        currentRow = 0  #holds the current map row we are working on (y)
        currentTile = 0 #holds the current tile we are working on (x)

        # a bit of Black magic to perform movement animations
        if moved != None:
            steps = len(self.tiles[moved][m_type][self.creatures[moved][7]])    # number of steps depends on animation textures quantity
            stepDistance = (self.tileWidth/2)/steps # step distance in pixels depends on number of steps
            # a dict to map coordinate delta to pixel delta
            delta_map = {(0,0): (0,0), (-1,0): (-stepDistance,stepDistance), (1,0): (stepDistance,-stepDistance),
                    (0,-1): (-stepDistance,-stepDistance), (0,1):(stepDistance,stepDistance)}   # (y,x)
            # (-1,0) - w; (1,0) - s; (0,-1) - a; (0,1) - d


        draw_delta = (0,0)
        if cr_r != 0:
            draw_delta = delta_map[delta]

        if moved == '@':    # we are moving the whole map actually if it was player character which moved
            movemap_delta = (draw_delta[0]*(-cr_r), draw_delta[1]*(-cr_r))
            movechar_delta = (0,0)
        else:               # or just a single character else
            movemap_delta = (0,0)
            movechar_delta = (draw_delta[0]*cr_r, draw_delta[1]*cr_r)

        self.updDsight() # getting recent sight

        for row in self.dsight:
            for tile in row:
                if tile not in self.tiles.keys():
                    tileImage=self.default
                    self.updTile(currentTile, currentRow, self.tiles[' '][0], movemap_delta)
                    self.updTile(currentTile, currentRow, tileImage, movemap_delta)
                    currentTile += 1
                elif tile != moved:
                    # the tile may be not 'moved', but it may be the end point of movement..
                    if starting_tile != None and m_type == 'walk' and (currentTile,currentRow) == \
                            (starting_tile[0]+delta[1],starting_tile[1]+delta[0]) and cr_r > \
                            len(self.tiles[moved][m_type][self.creatures[moved][7]]):    # moving in 2nd tile
                        steps = (len(self.tiles[moved][m_type][self.creatures[moved][7]])-1)/2
                        reverse_delta = ((-stepDistance*steps)+draw_delta[0], (-stepDistance*steps)+draw_delta[1])
                        floor = getFloorTex()   # redraw floor texture
                        self.updTile(currentTile, currentRow, floor, movemap_delta)
                        if moved != '@':
                            tileImage = self.tiles[moved][m_type][self.creatures[moved][7]][cr_r/2]
                            self.updTile(currentTile-delta[1], currentRow-delta[0], tileImage, movechar_delta)
                        else:
                            drawPlayer(True, m_type, moved, movechar_delta)
                    else:
                        if tile == '1': # beyond the map
                            tileImage = self.tiles[tile]
                            self.updTile(currentTile, currentRow, tileImage, movemap_delta)
                        elif tile == ' ':
                            floor = getFloorTex()
                            self.updTile(currentTile, currentRow, floor, movemap_delta)
                        elif tile == '#':
                            coords = self.dsight_coords[currentRow][currentTile]
                            tile_tex = self.level_textures[coords[0]][coords[1]]
                            if str(type(tile_tex)) == "<type 'tuple'>":
                                self.updTile(currentTile, currentRow, self.tiles[' '][0], movemap_delta)
                                if self.isTp(coords[0], coords[1]):
                                    tileImage = self.walls_tp[tile_tex[0]][1][tile_tex[1]]
                                else:
                                    tileImage = self.walls[tile_tex[0]][1][tile_tex[1]]
                            else:
                                tileImage = self.blank
                            self.updTile(currentTile, currentRow, tileImage, movemap_delta)
                        elif tile in self.creatures.keys():
                            floor = getFloorTex()
                            self.updTile(currentTile, currentRow, floor, movemap_delta)
                            if tile != '@':
                                tileImage = self.tiles[tile]['walk'][self.creatures[tile][7]][0]
                                self.updTile(currentTile, currentRow, tileImage, movemap_delta)
                            else:
                                drawPlayer(False, 'walk', '@', movemap_delta, 0)
                        else:
                            tileImage = self.tiles[tile]    # CHANGE THIS WHEN CREATURE TEXTURES R READY!   # waht did I mean here...
                            floor = getFloorTex()
                            self.updTile(currentTile, currentRow, floor, movemap_delta)
                            self.updTile(currentTile, currentRow, tileImage, movemap_delta)

                    currentTile += 1
                else:
                    if m_type == 'walk':
                        tileImage = self.tiles[tile][m_type][self.creatures[tile][7]][cr_r/2]
                        starting_tile = (currentTile, currentRow)
                        floor = getFloorTex()
                        if cr_r > len(self.tiles[moved][m_type][self.creatures[moved][7]]):   # redrawing starting tile
                            self.updTile(currentTile, currentRow, floor, movemap_delta)
                        else:   # moving in starting tile
                            self.updTile(currentTile, currentRow, floor, movemap_delta)
                            if moved != '@':
                                self.updTile(currentTile, currentRow, tileImage, movechar_delta)
                            else:
                                drawPlayer(False, m_type, moved, movechar_delta)
                    else:
                        floor = getFloorTex()
                        self.updTile(currentTile, currentRow, floor, movemap_delta)
                        if moved != '@':
                            tileImage = self.tiles[tile][m_type][self.creatures[tile][7]][cr_r/2]
                            self.updTile(currentTile, currentRow, tileImage, movechar_delta)
                        else:
                            drawPlayer(False, m_type, moved, movechar_delta)
                    currentTile += 1
            currentTile = 0 #reset the current working tile to 0 (we're starting a new row remember so we need to render the first tile of that row at index 0)
            currentRow += 1 #increment the current working row so we know we're starting a new row (used for calculating the y coord for the tile)


        #ren = (self.sight_range*2)+5
        #borders = range(ren)[:2] + range(ren)[-1:]
        #for row in range(ren):
        #    for tile in range(ren):
        #        if row in borders or tile in borders:
        #            self.updTile(tile, row, self.black)

        self.DISPLAYSURF.blit(self.fog, (0, 0))   # Draw text bg
        if moved != None:
            if cr_r % len(self.tiles[moved][m_type][self.creatures[moved][7]]) == 0 and m_type == 'walk':
                self.playEffect('steps')
            self.DISPLAYSURF.blit(self.gamelog_bg, (0, 570))   # Draw text bg
            self.drawText(self.messages, 570)
            self.reDraw()
            self.DISPLAYSURF.fill(((0,0,0)))
            cr_r += 1
            if cr_r < len(self.tiles[moved][m_type][self.creatures[moved][7]])*2:
                if m_type == 'attack':
                    if cr_r == len(self.tiles[moved][m_type][self.creatures[moved][7]])/2:
                        self.playEffect('hits')
                    self.sleep(self.anim_del)
                self.tileLogic(moved, delta, cr_r, starting_tile, m_type)


    def fullscMsg(self, txt, delta_y = 0):
        '''
        displays txt full screen
        '''
        self.DISPLAYSURF.blit(self.bg, (0, 0))   # Draw text bg
        self.drawText(txt, delta_y)
        self.reDraw()

        kbd_inp = ''
        while kbd_inp == '':
            event = self.pygame.event.poll()
            if event.type == self.pygame.KEYDOWN:
                kbd_inp = (self.pygame.key.name(event.key))
