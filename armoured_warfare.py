#15-112
#Eric Yu
#Section D

#Tank movement modified off of code provided by Richard Jones in Rapid Game
#(Got rid of acceleration and made the tanks slower)
#Development with Python (http://richard.cgpublisher.com/product/pub.84/
#prod.11).  Some of the run function was also modified from Richard Jones
#as well (mostly tank movement, clearing, and updating).

#The delay in between shots was modified from the code on
#http://thepythongamebook.com/en:pygame:step020.

#Camera movements based off of code from
#http://www.shemseddine.com/2013/03/06/pygame-map-scrolling-for-rpg-games/

#Tank information in the selection screen taken from Wikipedia.

#Various images taken from Google Images, including:
#http://i.imgur.com/bJRlL63.jpg
#http://opengameart.org/sites/default/files/styles/watermarked/public/tanks.png
#http://i.dailymail.co.uk/i/pix/2011/11/10/
#   article-2059745-000043A000000CB2-688_634x319.jpg
#http://images5.alphacoders.com/321/321115.jpg
#http://www.juniorgeneral.org/donated/2008/nov21/desert2.gif
#https://cdn.tutsplus.com/active/uploads/legacy/premium/014_teaser/21.jpg
#Wikipedia (especially for the tanks)
#http://www.ifelix.net/gamingblog/wp-content/uploads//2012/01/hotchkiss.jpg
#http://www.xnadevelopment.com/livewriter/NotsoHealthy_12BC1/HealthBar2.png

#Various sound clips taken from Youtube, including:
#Call of Duty Songs from Treyarch
#https://www.youtube.com/watch?v=gEUwXgMJpFc
#https://www.youtube.com/watch?v=IGN4oYd4vwU
#https://www.youtube.com/watch?v=hSIjZ2F-eDQ
#https://www.youtube.com/watch?v=wB5cLdyjx1U
#https://www.youtube.com/watch?v=SIxOl1EraXA
#https://www.youtube.com/watch?v=TVkqVlQ-8ZM
#https://www.youtube.com/watch?v=RuY86YXEZZY
#https://www.youtube.com/watch?v=1kooXAfY7p8
#https://www.youtube.com/watch?v=h3-ncacT5OM

#I hope you guys enjoy!  ~Eric Yu


#########################################################################
#####                        ARMOURED WARFARE                       #####
#########################################################################

import pygame, math, sys, time, random
from pygame.locals import *

#########################################################################
#####      Tank, Turret, Shell, and Building Classes                #####
#########################################################################

class TankSprite(pygame.sprite.Sprite):
    #Draws the tank
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image).convert_alpha()
        self.position = position
        self.speed = self.direction = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0
        self.MAX_FORWARD_SPEED = 1
        self.MAX_REVERSE_SPEED = 1
        self.TURN_SPEED = 1
        self.rect= self.src_image.get_rect()

    def update(self, deltat):
        self.speed = (self.k_up + self.k_down)
        #Cannot exceed a certain speed
        if self.speed > self.MAX_FORWARD_SPEED:
            self.speed = self.MAX_FORWARD_SPEED
        if self.speed < -self.MAX_REVERSE_SPEED:
            self.speed = -self.MAX_REVERSE_SPEED
        self.direction += (self.k_right + self.k_left)
        x, y = self.position
        #Allows the tank to turn
        rad = self.direction * math.pi/180
        x+= -self.speed*math.sin(rad)
        y += -self.speed*math.cos(rad)
        self.position = (x, y)
        self.image = pygame.transform.rotate(self.src_image, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position


class turret(pygame.sprite.Sprite):
    #controls the turret, which follows the tank's chassis
    MAX_FORWARD_SPEED = 10
    MAX_REVERSE_SPEED = 10
    TURN_SPEED = 5

    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image).convert_alpha()
        self.rect= self.src_image.get_rect()
        self.position = position
        self.speed = self.direction = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0
        self.mouseX, self.mouseY = 0, 0
        self.angle = math.pi/2
        self.timeFired = 3 
        self.fire = 0.0

    def update(self, deltat):
        self.speed = (self.k_up + self.k_down)
        #Cannot exceed a certain speed
        if self.speed > self.MAX_FORWARD_SPEED:
            self.speed = self.MAX_FORWARD_SPEED
        if self.speed < -self.MAX_REVERSE_SPEED:
            self.speed = -self.MAX_REVERSE_SPEED
        self.direction += (self.k_right + self.k_left)
        x, y = self.position
        #Allows the tank to turn
        rad = self.direction * math.pi/180
        x+= -self.speed*math.sin(rad)
        y += -self.speed*math.cos(rad)
        self.position = (x, y)
        self.turn()
        self.image = pygame.transform.rotate(self.src_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.position[0], self.position[1])

    def turn(self):
        self.angle = math.atan2(self.position[0]-self.mouseX,
                           self.position[1]-self.mouseY)
        self.angle = math.degrees(self.angle)


class wall(pygame.sprite.Sprite):
    #Creates an obstacle
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image).convert_alpha()
        self.position = position
        self.image = self.src_image
        self.rect = self.image.get_rect()

    def update(self, deltat):
        self.image = self.src_image
        self.rect = self.image.get_rect()
        self.rect.center = self.position

class shell(turret):
    #controls the turret, which follows the tank's chassis
    MAX_FORWARD_SPEED = 15
    MAX_REVERSE_SPEED = 15
    TURN_SPEED = 5

    def __init__(self, image, position, angle):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image).convert_alpha()
        self.position = position
        self.mouseX, self.mouseY = 0, 0
        self.angle = angle
        self.vel = 10
        self.dx = math.cos(math.radians(self.angle)) * self.vel
        self.dy = math.sin(math.radians(self.angle)) * self.vel


    def update(self, seconds = 0.0):
        x, y = self.position
        y+= -self.dx
        x += -self.dy
        self.position = (x, y)
        self.image = pygame.transform.rotate(self.src_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

#########################################################################
#####      Health Bar and Ammo Classes                              #####
#########################################################################


class healthBar(pygame.sprite.Sprite):
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image).convert_alpha()
        self.position = position
        self.image = self.src_image
        self.rect = self.image.get_rect()

    def update(self, deltat):

        self.image = pygame.transform.scale(self.src_image, (200, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        
class shellImage(pygame.sprite.Sprite):
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image).convert_alpha()
        self.position = position
        self.image = self.src_image
        self.rect = self.image.get_rect()

    def update(self, deltat):
        self.image = self.src_image
        self.rect = self.image.get_rect()
        self.rect.center = self.position

#########################################################################
#####      Running the Main Menu                                    #####
#########################################################################

class runMainMenu(object):
    def __init__(self):
        pygame.init()
        self.isRunning = True
        self.screen = pygame.display.set_mode((900, 600), 0, 32)
        self.menuBackground = pygame.image.load('Title Screen1.png'
                                                ).convert_alpha()
        self.menuBackgroundRect = self.screen.get_rect()
        pygame.mixer.init(frequency=22050, size=-16,
                               channels=1, buffer=4096)
        
        self.info = pygame.image.load('info1.png').convert_alpha()
        self.info2 = pygame.image.load('info2.png').convert_alpha()
        self.infoRect = self.screen.get_rect()
        self.info2Rect = self.screen.get_rect()
        self.notInfo = True


    def menuRun(self):
        pygame.mixer.music.load("Call_Of_Duty_3_Menu_Theme.wav")
        pygame.mixer.music.play(-1,0.0)
        pygame.mixer.music.set_volume(1)
        while True:
            if self.isRunning == False:
                break
            if self.notInfo:
                self.screen.blit(self.menuBackground, (0,0))
            for event in pygame.event.get():
                if hasattr(event, 'key'):
                    if event.key == K_RETURN:
                        tankSelection().tankSelectionRun()
                    elif event.key == K_i:
                        self.screen.blit(self.info, (0, 0))
                        self.notInfo = False
                    elif event.key == K_r:
                        self.notInfo = True
                    elif event.key == K_RIGHT:
                        if self.notInfo == False:
                            self.screen.blit(self.info2, (0,0))
                        else:
                            pass
                    elif event.key == K_LEFT:
                        if self.notInfo == False:
                            self.screen.blit(self.info, (0, 0))
                        else:
                            pass
                    elif event.key == K_q:
                        self.isRunning = False
                if event.type == pygame.QUIT:
                    self.isRunning = False
            pygame.display.flip()
        pygame.quit()

#########################################################################
#####      Selecting a Tank                                         #####
#########################################################################

class tankSelection(object):
    def __init__(self):
        pygame.init()
        self.isRunning = True
        self.screen = pygame.display.set_mode((900, 600), 0, 32)
        self.tankBackground = pygame.image.load('TankSelection1.png'
                                                ).convert_alpha()
        self.selected = pygame.image.load('selected.png').convert_alpha()
        self.tankBackgroundRect = self.screen.get_rect()
        pygame.font.init()
        self.tankImg1 = pygame.image.load('hotchkissTankImg.png'
                                          ).convert_alpha()
        self.tankImg2 = pygame.image.load('t34tankimg.png').convert_alpha()
        self.tankImg3 = pygame.image.load('panzerivimg.png').convert_alpha()
        self.tankImg4 = pygame.image.load('pantherimg.png').convert_alpha()
        self.tankImg1Rect = self.screen.get_rect()
        self.tankImg2Rect = self.screen.get_rect()
        self.tankImg3Rect = self.screen.get_rect()
        self.tankImg4Rect = self.screen.get_rect()
        self.isTankImg1 = False
        self.isTankImg2 = False
        self.isTankImg3 = False
        self.isTankImg4 = False


    def tankSelectionRun(self):
        chassis = ''
        cannon = ''
        while True:
            if self.isRunning == False:
                break
            if chassis == '':
                self.screen.blit(self.tankBackground, (0,0))
            else:
                self.screen.blit(self.selected, (0,0))
            if self.isTankImg1 == True:
                self.screen.blit(self.tankImg1, (450, 65))
                chassis = 'armor1.png'
                cannon = 'chassis1.png'
            elif self.isTankImg2 == True:
                self.screen.blit(self.tankImg2, (450, 65))
                chassis = 't34chassis.png'
                cannon = 't34Turret1.png'
            elif self.isTankImg3 == True:
                self.screen.blit(self.tankImg3, (450, 65))
                chassis = 'chassis2.png'
                cannon = 'panzerTurret.png'
            elif self.isTankImg4 == True:
                self.screen.blit(self.tankImg4, (450, 65))
                chassis = 'pantherchassis.png'
                cannon = 'pantherfire.png'
            for event in pygame.event.get():
                if hasattr(event, 'key'):
                    if event.key == K_SPACE:
                        if chassis != '' and cannon != '':
                            armouredWarfare(0, 0, chassis, cannon).run()
                        else:
                            pass
                    elif event.key == K_r:
                        game = runMainMenu()
                        game.menuRun()
                        
                    elif event.key == K_h:
                        self.isTankImg1 = True
                        self.isTankImg2 = False
                        self.isTankImg3 = False
                        self.isTankImg4 = False
                    elif event.key == K_t:
                        self.isTankImg1 = False
                        self.isTankImg2 = True
                        self.isTankImg3 = False
                        self.isTankImg4 = False
                    elif event.key == K_z:
                        self.isTankImg1 = False
                        self.isTankImg2 = False
                        self.isTankImg3 = True
                        self.isTankImg4 = False
                    elif event.key == K_p:
                        self.isTankImg1 = False
                        self.isTankImg2 = False
                        self.isTankImg3 = False
                        self.isTankImg4 = True
                        
                    elif event.key == K_q:
                        self.isRunning = False
                if event.type == pygame.QUIT:
                    self.isRunning = False
            pygame.display.flip()
        pygame.quit()
        sys.exit()

#########################################################################
#####      Victory and Defeat Screens                               #####
#########################################################################

class victory(object):
    def __init__(self):
        pygame.init()
        self.isRunning = True
        self.screen = pygame.display.set_mode((900, 600), 0, 32)
        self.victoryBackground = pygame.image.load('victory.png'
                                                   ).convert_alpha()
        self.victoryBackgroundRect = self.screen.get_rect()

    def victoryRun(self):
        while True:
            if self.isRunning == False:
                break
            self.screen.blit(self.victoryBackground, (0,0))
            for event in pygame.event.get():
                if hasattr(event, 'key'):
                    if event.key == K_r:
                        game = runMainMenu()
                        game.menuRun()
                    elif event.key == K_q:
                        self.isRunning = False

                if event.type == pygame.QUIT:
                    self.isRunning = False

            pygame.display.flip()
        pygame.quit()
        sys.exit()

class defeat(object):
    def __init__(self):
        pygame.init()
        self.isRunning = True
        self.screen = pygame.display.set_mode((900, 600), 0, 32)
        self.defeatBackground = pygame.image.load('defeat.png'
                                                   ).convert_alpha()
        self.defeatBackgroundRect = self.screen.get_rect()

    def defeatRun(self):
        while True:
            if self.isRunning == False:
                break
            self.screen.blit(self.defeatBackground, (0,0))
            for event in pygame.event.get():
                if hasattr(event, 'key'):
                    if event.key == K_r:
                        game = runMainMenu()
                        game.menuRun()
                    elif event.key == K_q:
                        self.isRunning = False
                if event.type == pygame.QUIT:
                    self.isRunning = False
            pygame.display.flip()
        pygame.quit()
        sys.exit()
            

#########################################################################
#####      The Main Game                                            #####
#########################################################################
            

class armouredWarfare(object):
    #Runs the game
    def __init__(self, yourScore, enemyScore, chassis, cannon):
        pygame.init()

        self.chassis = chassis
        self.cannon = cannon

        self.screen = pygame.display.set_mode((900, 600), 0, 32)
        
        self.background = pygame.image.load('desert2.gif').convert_alpha()
        self.backgroundRect = self.screen.get_rect()

        canvasLength = 900
        canvasWidth = 600
        
        self.clock = pygame.time.Clock()
        self.rect = self.screen.get_rect()

        self.x, self.y = self.rect.center

        self.mouseX, self.mouseY = 0, 0

        #Random Player Position
        tankx = random.randint(0, canvasLength)
        tanky = random.randint(0, canvasWidth)

        player = (tankx, tanky)

        self.tank = TankSprite(self.chassis, player)
        self.tank_group = pygame.sprite.RenderPlain(self.tank)
        self.tank_group.update(30)

        self.turret = turret(self.cannon, player)
        self.turret_group = pygame.sprite.RenderPlain(self.turret)
        
        #Random Enemy Position
        enemyTankx = random.randint(0, canvasLength)
        enemyTanky = random.randint(0, canvasWidth)

        #Randomize Enemies

        enemyList = ['armor1.png', 't34chassis.png', 'chassis2.png',
                     'pantherchassis.png']
        enemyTurretList = ['chassis1.png', 't34Turret1.png',
                           'panzerTurret.png',
                           'pantherfire.png']
        enemyNum = random.randint(0, len(enemyList)-1)

        self.enemyTankType = enemyList[enemyNum]
        self.enemyTurretType = enemyTurretList[enemyNum]

        self.enemyTank = TankSprite(
            self.enemyTankType, (enemyTankx, enemyTanky))
        self.enemyTank_group = pygame.sprite.RenderPlain(self.enemyTank)

        self.enemyTurret = turret(self.enemyTurretType
                                  , (enemyTankx, enemyTanky))
        self.enemyTurret_group = pygame.sprite.RenderPlain(self.enemyTurret)

        
        self.shell_group = pygame.sprite.RenderPlain()

        self.enemyShell_group = pygame.sprite.RenderPlain()

        #enemy attributes

        if self.enemyTankType == 'armor1.png':
            self.enemyHealth = 80
            self.enemyTimeFired = 600
            self.enemyDamage = 10
            self.enemyGo = .35

        elif self.enemyTankType == 't34chassis.png':
            self.enemyHealth = 100
            self.enemyTimeFired = 850
            self.enemyDamage = 20
            self.enemyGo= .25

        elif self.enemyTankType == 'chassis2.png':
            self.enemyHealth = 120
            self.enemyTimeFired = 850
            self.enemyDamage = 15
            self.enemyGo = .25

        elif self.enemyTankType == 'pantherchassis.png':
            self.enemyHealth = 150
            self.enemyTimeFired = 1200
            self.enemyDamage = 25
            self.enemyGo = .10

        

        #Health Bars and Shell

        self.healthBar = healthBar('HealthBar11.png', (120, 30))
        
        self.healthBar_group = pygame.sprite.RenderPlain(self.healthBar)

        self.enemyHealthBar = healthBar('HealthBar11.png', (780, 30))

        self.enemyHealthBar_group = pygame.sprite.RenderPlain(
            self.enemyHealthBar)

        self.shellImage = shellImage('shell1.png', (800, 500))
        self.shellImage_group = pygame.sprite.RenderPlain(self.shellImage)

        self.soundsInit()

        #Different classes of tanks

        if self.chassis == 'armor1.png':
            self.health = 80
            self.timeFired = 350
            self.damage = 10
            self.go = 1.0

        elif self.chassis == 't34chassis.png':
            self.health = 100
            self.timeFired = 500
            self.damage = 20
            self.go= .75

        elif self.chassis == 'chassis2.png':
            self.health = 120
            self.timeFired = 500
            self.damage = 15
            self.go = .75

        elif self.chassis == 'pantherchassis.png':
            self.health = 150
            self.timeFired = 650
            self.damage = 25
            self.go = .5


        self.obstacles = []
        self.walls = []

        self.isRunning = True

        numberOfObstacles = random.randint(1, 7)

        self.fire = 0.0

        self.enemyFire = 300.0

        self.enemyTurned = 1000

        self.turn = 0.0

        self.turning = 0.0
        self.enemyTurning = 100

        #Did you win or lose the game?
        self.gameOver = False

        #Display score
        self.yourScore = yourScore
        self.enemyScore = enemyScore
        self.oppScore = False
        self.uScore = False

        #Victory or Defeat?
        if self.yourScore == 3:
            victory().victoryRun()

        elif self.enemyScore == 3:
            defeat().defeatRun()

        #Initiates obstacles

        for obstacle in xrange(numberOfObstacles):
            #Creates random number of obstacles
            x = random.randint(0, canvasLength)
            y = random.randint(0, canvasWidth)
            self.wall = wall('building.png', (x, y))
            self.wall.update(30)
            self.enemyTank.update(30)
            self.tank.update(30)
            if (pygame.sprite.collide_rect(self.tank, self.wall) or
                pygame.sprite.collide_rect(self.enemyTank, self.wall) or
                pygame.sprite.collide_rect(self.enemyTank, self.tank)):
                
                armouredWarfare(self.yourScore, self.enemyScore, self.chassis,
                                self.cannon).run()
            for i in self.walls:
                if (pygame.sprite.collide_rect(self.wall, i)):
                    armouredWarfare(self.yourScore, self.enemyScore,
                                    self.chassis,
                                self.cannon).run()
                    
                
            self.wall_group = pygame.sprite.RenderPlain(self.wall)
            self.obstacles += [self.wall_group]
            self.walls += [self.wall]
            #possibility that tank will spawn in building

        #Background music
        pygame.mixer.init(frequency=22050, size=-16,
                               channels=4, buffer=4096)
        pygame.mixer.music.load("[HD_[STEREO_War_Ambient_Sounds.wav")
        
        #deltat is 30 frames per second
        self.deltat = 30
        
    def soundsInit(self):
        class Struct(): pass
        self.sounds = Struct()
        self.sounds.crash = pygame.mixer.Sound(
            'Logo_Impact_Bang_Sound_effect.wav')
        self.sounds.crash.set_volume(0.1)
        self.sounds.tankFire = pygame.mixer.Sound('Tank_Sound_Effect.wav')
        

        
#Tank AI controls
    def enemyTurretRun(self):
        #How the enemy follows and attacks you
        (self.enemyTurret.mouseX,
         self.enemyTurret.mouseY) = (self.tank.position[0],
                                     self.tank.position[1])
        if (self.enemyFire == 0):
            self.enemyFire = self.enemyTimeFired
            self.sounds.tankFire.play()
            angle = math.atan2(
                self.enemyTank.position[0]-self.tank.position[0],
                               self.enemyTank.position[1]
                               -self.tank.position[1])
            angle = math.degrees(angle)
            self.enemyShell_group.add(shell('shell2.png',
                                                 self.enemyTank.position,angle))

    def enemyTankRun(self):
        if self.gameOver == False:
            #self.sounds.movement.play()
            pass
        if self.tank.position[1] > self.enemyTank.position[1]:
            self.enemyTank.k_down = self.enemyGo
            self.enemyTurret.k_down = self.enemyGo

        elif self.tank.position[1] < self.enemyTank.position[1]:
            self.enemyTank.k_up = self.enemyGo
            self.enemyTurret.k_up = self.enemyGo

        elif self.tank.position[1] == self.enemyTank.position[1]:
            self.enemyTank.k_up = 0
            self.enemyTurret.k_up = 0

        if pygame.sprite.collide_rect(self.tank, self.enemyTank) == True:
            self.enemyTank.k_down = 0
            self.enemyTank.k_up = 0
            self.enemyTank.k_right = 0
            self.enemyTank.k_left = 0
            self.enemyTurret.k_down = 0
            self.enemyTurret.k_up = 0
            self.enemyTurret.k_right = 0
            self.enemyTurret.k_left = 0
            
        for wall in self.walls:
            if pygame.sprite.collide_rect(self.enemyTank, wall) == True:
                
                self.enemyTank.k_up = 0
                self.enemyTank.k_down = 0
                self.enemyTank.k_right = 0
                self.enemyTank.k_left = 0
                self.enemyTurret.k_up = 0
                self.enemyTurret.k_down = 0
                self.enemyTurret.k_right = 0
                self.enemyTurret.k_left = 0



    def enemyTankTurn(self):
        self.enemyTank.direction = math.atan2(
            self.enemyTank.position[0]-self.tank.position[0],
                               self.enemyTank.position[1]
                               -self.tank.position[1])/(math.pi/180)
        self.enemyTurret.direction = math.atan2(
            self.enemyTank.position[0]-self.tank.position[0],
                               self.enemyTank.position[1]
                               -self.tank.position[1])/(math.pi/180)
            

    def shotsFired(self):
        self.shellImage = shellImage('shellTrans.png', (800, 500))
        self.shellImage_group = pygame.sprite.RenderPlain(self.shellImage)

    def shotsKept(self):
        self.shellImage = shellImage('shell1.png', (800, 500))
        self.shellImage_group = pygame.sprite.RenderPlain(self.shellImage)

    def displayScore(self, yourScore, enemyScore):
        pygame.font.init()
        myfont = pygame.font.SysFont("monospace", 15, True)
        self.myScore = myfont.render("Your Score: %d" % (yourScore), 1, (0,0,0))
        self.theirScore = myfont.render(
            "Enemy Score: %d" % (enemyScore), 1, (0,0,0))
        self.screen.blit(self.myScore, (250,20))
        self.screen.blit(self.theirScore, (530, 20))

    def score(self):
        if self.oppScore == True:
            self.enemyScore+=1
            self.oppScore = False
        elif self.uScore == True:
            self.yourScore += 1
            self.uScore = False

    def run(self):
        self.playing = True
        self.clock.tick(self.deltat)
        pygame.font.init()
        clock = pygame.time.Clock()

        deltat = self.deltat
        shotsFired = False
        #loops background music
        pygame.mixer.music.set_volume(0.10)
        pygame.mixer.music.play(-1,0.0)
        
        while True:

            if self.isRunning == False:
                break
                
            self.screen.blit(self.background, (0,0))

            if self.turn > 0:
                self.turn -=1
            elif self.turn < 0:
                self.turn = 0

            if self.fire == 0:
                self.shotsKept()
            if self.fire > 0:
                self.fire -= 1
            elif self.fire < 0:
                self.fire = 0
            if self.enemyFire > 0:
                self.enemyFire -= 1
            elif self.enemyFire < 0:
                self.enemyFire = 0

            if self.turn > 0:
                self.turn -= 1
            elif self.turn < 0:
                self.turn = 0

            if self.turning > 0:
                self.turning -= 1
            elif self.turning < 0:
                self.turning = 0

            self.enemyTankRun()


            self.enemyTankTurn()

            for event in pygame.event.get():
                if hasattr(event, 'key'):
                    if self.gameOver == False:
                    #moves and turns the tank around
                        down = event.type == KEYDOWN
                        if event.key == K_d:
                            self.tank.k_right =down*-self.go
                            self.turret.k_right =down*-self.go

                        elif event.key == K_a:
                            self.tank.k_left = down * self.go
                            self.turret.k_left = down * self.go


                        elif event.key == K_s:
                            self.tank.k_down = down * -self.go
                            self.turret.k_down = down * -self.go


                        elif event.key == K_w:
                            self.tank.k_up = down * self.go
                            self.turret.k_up = down * self.go

                    if event.key == K_r:
                        pygame.mixer.stop()
                        game = runMainMenu()
                        game.menuRun()

                    elif event.key == K_RETURN:
                        if self.uScore == True:
                            armouredWarfare(self.yourScore+1, self.enemyScore,
                                            self.chassis, self.cannon).run()
                        elif self.oppScore == True:
                            armouredWarfare(self.yourScore, self.enemyScore+1,
                                            self.chassis, self.cannon).run()
                        

                    elif event.key == K_q:
                        self.isRunning = False


                if event.type == pygame.QUIT:
                    self.isRunning = False

                
                if event.type == pygame.MOUSEMOTION:
                    #To be used to control the turret
                    (self.turret.mouseX,
                     self.turret.mouseY) = pygame.mouse.get_pos()
                    (self.mouseX,
                     self.mouseY) = pygame.mouse.get_pos()
                if (self.fire == 0):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        #Fires the cannon and plays its sound effect
                        if event.button == 1:

                            self.fire = self.timeFired

                            if self.fire != 0:
                                self.shotsFired()
                                
                                self.sounds.tankFire.play()
                                
                                angle = math.atan2(self.tank.position[0]
                                                   -self.mouseX,
                                   self.tank.position[1]-self.mouseY)
                                angle = math.degrees(angle)
                                self.shell_group.add(
                                    shell('shell2.png',
                                          self.tank.position, angle))
            #enemy tank movement
            if self.gameOver == False:
                self.enemyTurretRun()
          
            #erases all the elements on screen

            self.tank_group.clear(self.screen, self.background)
            self.shell_group.clear(self.screen, self.background)
            self.turret_group.clear(self.screen, self.background)
            self.enemyTank_group.clear(self.screen, self.background)
            self.enemyTurret_group.clear(self.screen, self.background)
            self.enemyShell_group.clear(self.screen, self.background)
            
            
            for i in self.obstacles:
                i.clear(self.screen, self.background)

            self.shellImage_group.clear(self.screen, self.background)
            self.healthBar_group.clear(self.screen, self.background)
            self.enemyHealthBar_group.clear(self.screen, self.background)
            
            #Updates the different objects
            self.tank_group.update(deltat)
            self.shell_group.update(deltat)
            self.turret_group.update(deltat)
            self.enemyTank_group.update(deltat)
            self.enemyTurret_group.update(deltat)
            self.enemyShell_group.update(deltat)
            
            for i in self.obstacles:
                i.update(deltat)
            self.shellImage_group.update(deltat)
            self.healthBar_group.update(deltat)
            self.enemyHealthBar_group.update(deltat)
            
            #Redraws everything onto the screen
            self.tank_group.draw(self.screen)
            self.shell_group.draw(self.screen)
            self.turret_group.draw(self.screen)
            self.enemyTank_group.draw(self.screen)
            self.enemyTurret_group.draw(self.screen)
            self.enemyShell_group.draw(self.screen)
            
            for i in self.obstacles:
                i.draw(self.screen)
            self.shellImage_group.draw(self.screen)
            self.healthBar_group.draw(self.screen)
            self.enemyHealthBar_group.draw(self.screen)


            #Detects collision and stops the movement of the tank
            for i in self.walls:
                if pygame.sprite.collide_rect(self.tank, i) == True:
                    #Takes damage once you collide with a building
                    if (self.tank.k_up != 0 or self.tank.k_down != 0 or
                        self.tank.k_left != 0 or self.tank.k_right != 0):
                        self.health -=10

                    self.tank.k_down = 0
                    self.tank.k_up = 0
                    self.tank.k_right = 0
                    self.tank.k_left = 0
                    self.turret.k_down = 0
                    self.turret.k_up = 0
                    self.turret.k_right = 0
                    self.turret.k_left = 0

                    self.sounds.crash.play()
                    
                #If the shots go out of the screen or hit a building...
                for j in self.shell_group:
                    if pygame.sprite.collide_rect(j, i) == True:
                        self.sounds.crash.play()
                        j.kill()
                    elif (j.position[0] < 0 or
                          j.position[1] < 0 or
                          j.position[0] > 900 or
                          j.position[1] > 600):
                        j.kill()

                for strike in self.enemyShell_group:
                    if pygame.sprite.collide_rect(strike, i) == True:
                        self.sounds.crash.play()
                        strike.kill()
                    elif (strike.position[0] < 0 or
                          strike.position[1] < 0 or
                          strike.position[0] > 900 or
                          strike.position[1] > 600):
                        strike.kill()

            if pygame.sprite.collide_rect(self.tank, self.enemyTank) == True:
                self.tank.k_down = 0
                self.tank.k_up = 0
                self.tank.k_right = 0
                self.tank.k_left = 0
                self.turret.k_down = 0
                self.turret.k_up = 0
                self.turret.k_right = 0
                self.turret.k_left = 0

                self.enemyTank.k_down = 0
                self.enemyTank.k_up = 0
                self.enemyTank.k_right = 0
                self.enemyTank.k_left = 0
                self.enemyTurret.k_down = 0
                self.enemyTurret.k_up = 0
                self.enemyTurret.k_right = 0
                self.enemyTurret.k_left = 0

                self.sounds.crash.play()

            for shot in self.shell_group:
                if self.enemyTank and pygame.sprite.collide_rect(
                    self.enemyTank, shot):
                    shot.kill()
                    self.enemyHealth -= self.damage

            for shot in self.enemyShell_group:
                if self.tank and pygame.sprite.collide_rect(self.tank, shot):
                    shot.kill()
                    self.health -= self.enemyDamage                    


            #Health Font
            healthFont = pygame.font.SysFont('monospace', 20, True)
            
            if self.chassis == "t34chassis.png":
                self.hPfont = healthFont.render("%d/100"%(self.health)
                                           , 1, (255,255,255))
                self.screen.blit(self.hPfont, (20,40))

                pygame.draw.rect(self.screen, (17, 81, 15),
                                 (23, 23, self.health*2-5,
                                                             14))
            elif self.chassis == "armor1.png":
                self.hPfont = healthFont.render("%d/80"%(self.health)
                                           , 1, (255,255,255))
                self.screen.blit(self.hPfont, (20,40))

                pygame.draw.rect(self.screen, (17, 81, 15),
                                 (23, 23, self.health*10/4-5,
                                                             14))
            elif self.chassis == "chassis2.png":
                self.hPfont = healthFont.render("%d/120"%(self.health)
                                           , 1, (255,255,255))
                self.screen.blit(self.hPfont, (20,40))

                pygame.draw.rect(self.screen, (17, 81, 15),
                                 (23, 23, self.health*5/3-5,
                                                             14))
            elif self.chassis == "pantherchassis.png":
                self.hPfont = healthFont.render("%d/150"%(self.health)
                                           , 1, (255,255,255))
                self.screen.blit(self.hPfont, (20,40))

                pygame.draw.rect(self.screen, (17, 81, 15),
                                 (23, 23, self.health*4/3-5,
                                                             14))
                
                

            #Enemy Health
            enemyhealthFont = pygame.font.SysFont('monospace', 15, True)

            self.enemyfont = enemyhealthFont.render("Enemy Health", 1,
                                                    (255,255,255))
            self.screen.blit(self.enemyfont, (680,38))

            if self.enemyTankType == 't34chassis.png':
                pygame.draw.rect(self.screen, (17, 81, 15),
                                 (683, 23, self.enemyHealth*2-5,
                                                             14))
            elif self.enemyTankType == 'armor1.png':
                pygame.draw.rect(self.screen, (17, 81, 15),
                                 (683, 23, self.enemyHealth*10/4-5,
                                                             14))

            elif self.enemyTankType == 'chassis2.png':
                pygame.draw.rect(self.screen, (17, 81, 15),
                                 (683, 23, self.enemyHealth*5/3-5,
                                                             14))

            elif self.enemyTankType == 'pantherchassis.png':
                pygame.draw.rect(self.screen, (17, 81, 15),
                                 (683, 23, self.enemyHealth*4/3-5,
                                                             14))
            

            #ammo regeneration tracker
            ammoFont = pygame.font.SysFont('monospace', 20, True)

            if self.fire == 0:
                self.amReady = ammoFont.render("Ready!", 1, (255, 255, 255))
                self.screen.blit(self.amReady, (720, 550))
            else:
                pygame.draw.rect(self.screen, (52,11,2), (720, 530, self.fire/5,
                                                            14))
            #self.screen.blit(self.amFont, (720,530))


            self.displayScore(self.yourScore, self.enemyScore)

            #Enemy Tank marker
            (mX, mY) = self.enemyTank.position 
            pygame.draw.circle(self.screen, (133, 8, 8),
                               (int(mX), int(mY-50)), 5)
            
            #When you win...
            if self.enemyHealth <= 0:
                self.enemyTank.kill()
                self.enemyTurret.kill()
                self.enemyTank_group.remove(self.enemyTank)
                self.enemyTurret_group.remove(self.enemyTurret)
                self.gameOver = True
                self.uScore = True
                self.sounds.crash.stop()
                pygame.mixer.stop()

                #Displays Victory Window
                if self.chassis == 'armor1.png':
                    
                    if self.playing == True:
                        pygame.mixer.music.load(
                        'Mireille_Mathieu_singing_La_Marseillaise_with_lyri.wav'
                        )
                        pygame.mixer.music.play(-1,0.0)
                        pygame.mixer.music.set_volume(1)
                        self.playing = False
                    
                    self.victoryBackground = pygame.image.load(
                        'hotchkiss_win.png').convert_alpha()
                    self.victoryBackgroundRect = self.screen.get_rect()
                elif self.chassis == 't34chassis.png':
                    if self.playing == True:
                        pygame.mixer.music.load(
                        'National_Anthem_of_the_Soviet_Union_-_1944_-_Red_A.wav'
                            )
                        pygame.mixer.music.play(-1,0.0)
                        pygame.mixer.music.set_volume(1)
                        self.playing = False
                    self.victoryBackground = pygame.image.load(
                        'T-34_win.png').convert_alpha()
                    self.victoryBackgroundRect = self.screen.get_rect()
                elif self.chassis == 'chassis2.png':
                    if self.playing == True:
                        pygame.mixer.music.load(
                            'Wehrmacht_Victory_March_K_niggr_tzer_Marsch_m.wav')
                        pygame.mixer.music.play(-1,0.0)
                        pygame.mixer.music.set_volume(1)
                        
                        self.playing = False
                    self.victoryBackground = pygame.image.load(
                            'panzer_win.png').convert_alpha()
                    self.victoryBackgroundRect = self.screen.get_rect()
                elif self.chassis == 'pantherchassis.png':
                    if self.playing == True:
                        pygame.mixer.music.load(
                            'German_Nazi_Party_Theme_HD.wav')
                        pygame.mixer.music.play(-1,0.0)
                        pygame.mixer.music.set_volume(1)
                        self.playing = False
                    self.victoryBackground = pygame.image.load(
                        'panther_win.png').convert_alpha()
                    self.victoryBackgroundRect = self.screen.get_rect()
                self.screen.blit(self.victoryBackground, (0, 0))
                
            #When you die...
            elif self.health <= 0:
                pygame.mixer.stop()
                self.tank.kill()
                self.turret.kill()
                if self.chassis == 'armor1.png':
                    self.lossBackground = pygame.image.load(
                        'hotchkiss_defeat.png').convert_alpha()
                    self.lossBackgroundRect = self.screen.get_rect()
                elif self.chassis == 't34chassis.png':
                    self.lossBackground = pygame.image.load(
                        'T34_Loss.png').convert_alpha()
                    self.lossBackgroundRect = self.screen.get_rect()
                elif self.chassis == 'chassis2.png':
                    self.lossBackground = pygame.image.load(
                        'Panzer_Loss.png').convert_alpha()
                    self.lossBackgroundRect = self.screen.get_rect()
                elif self.chassis == 'pantherchassis.png':
                    self.lossBackground = pygame.image.load(
                        'panther_loss.png').convert_alpha()
                    self.lossBackgroundRect = self.screen.get_rect()
                pygame.mixer.stop()
                if self.playing == True:
                    pygame.mixer.music.load('Sad_War_Music.wav')
                    pygame.mixer.music.play(-1,0.0)
                    pygame.mixer.music.set_volume(1)
                    self.playing = False
                self.screen.blit(self.lossBackground, (0, 0))
                self.gameOver = True
                self.oppScore = True
                self.sounds.crash.stop()

            #If you exit the playable area, reach the minefield!
            if (self.tank.position[0] < 0 or self.tank.position[0] > 900 or
                self.tank.position[1] < 0 or self.tank.position[1] > 600):
                pygame.font.init()
                mineFont = pygame.font.SysFont("monospace", 20, True)
                self.mineFont = mineFont.render(
                    "Get back soldier!  Minefield ahead!",
                                              1, (169, 11, 11))
                self.screen.blit(self.mineFont, (250, 580))
                
            if (self.tank.position[0]+60 < 0 or self.tank.position[0]-60 > 900
                or
                self.tank.position[1]+60 < 0 or self.tank.position[1]-60 > 600):
                self.sounds.tankFire.play()
                self.health = 0
                self.tank.kill()
                self.turret.kill()
                pygame.mixer.stop()
                if self.playing == True:
                    pygame.mixer.music.load('Sad_War_Music.wav')
                    pygame.mixer.music.play(-1,0.0)
                    pygame.mixer.music.set_volume(1)
                    self.playing = False
                if self.chassis == 'armor1.png':
                    self.lossBackground = pygame.image.load(
                        'hotchkiss_defeat.png').convert_alpha()
                    self.lossBackgroundRect = self.screen.get_rect()
                elif self.chassis == 't34chassis.png':
                    self.lossBackground = pygame.image.load(
                        'T34_Loss.png').convert_alpha()
                    self.lossBackgroundRect = self.screen.get_rect()
                elif self.chassis == 'chassis2.png':
                    self.lossBackground = pygame.image.load(
                        'Panzer_Loss.png').convert_alpha()
                    self.lossBackgroundRect = self.screen.get_rect()
                elif self.chassis == 'pantherchassis.png':
                    self.lossBackground = pygame.image.load(
                        'panther_loss.png').convert_alpha()
                    self.lossBackgroundRect = self.screen.get_rect()
                pygame.mixer.stop()
                self.screen.blit(self.lossBackground, (0, 0))
                self.gameOver = True
                self.oppScore = True

            
            pygame.display.flip()
        pygame.quit()
        sys.exit()

#########################################################################
#####      Running the Entire Game                                  #####
#########################################################################

game = runMainMenu()

game.menuRun()
    
