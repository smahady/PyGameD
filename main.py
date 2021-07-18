import pygame
from Background import Background
from Spritesheet import Spritesheet
from Ground import Ground
from enum import Enum
from tkinter import Tk, Button, Label
import random

class States(Enum):
	FALLING = 0
	WALK = 1
	JUMP = 2
	STAND = 3

class Facing():
	RIGHT = 0
	LEFT = 1

class Keys:
	# key variables
	K_ESC = 27
	K_SPACE = 32
	K_PGUP = 33
	K_PGDOWN = 34
	K_END = 35
	K_HOME = 36
	K_LEFT = 37
	K_UP = 38
	K_RIGHT = 39
	K_DOWN = 40



class Camera():
	def __init__(self, game):
		self.scene = game

	def follow(self, sprite):
		self.sprite = sprite

	def update(self):

		if self.sprite.drawX < 250:
			if self.sprite.posX < 300:
				self.sprite.posX = 300
			else:
				self.scene.offsetX -= 6
		if self.sprite.drawX > (350):
			if self.sprite.posX > (26*120):
				self.sprite.posX = (26*120)
			else:
				self.scene.offsetX += 6

class Spaceship(Spritesheet):
	def __init__(self, thisScene):
		super().__init__(thisScene, "sprites/spaceship100.png", 100, 100)
		self.posX = 300
		self.posY = 100
		self.dx = 6
		self.timer = 60
		self.enemies = []

	def update(self, offsetX, offsetY):
		super().update(offsetX, offsetY)
		if self.drawX < 0:
			self.dx = 6
		if self.drawX > 550:
			self.dx = -6
		self.timer -= 1
		if self.timer < 1:
			self.timer = 60
			self.enemySpawn()

		for enemy in self.enemies:
			enemy.update(self.game.offsetX, self.game.offsetY)

	def enemySpawn(self):
		temp = random.randint(0,2)
		newEnemy = 0
		if temp == 0:
			newEnemy = Enemy(self.game, self.posX, self.posY)
		elif temp==1:
			newEnemy = GroundEnemy(self.game, self.posX, self.posY)
		elif temp ==2:
			newEnemy = FlyingEnemy(self.game, self.posX, self.posY)
		self.enemies.append(newEnemy)
		self.game.sprites.add(newEnemy)

# Abstract base class - a base class we intend to inherit in another class
class BaseEnemy(Spritesheet):
	def __init__(self, thisScene, file, width, height, x, y):
		super().__init__(thisScene, file, width, height)
		self.posX = x
		self.posY = y
		self.dy = 3
		self.timer = 120
	def update(self, offsetX, offsetY):
		self.timer -= 1
		if self.timer < 1:
			self.makeDecision()
		super().update(offsetX, offsetY)
	def makeDecision(self):
		pass	

class Enemy(BaseEnemy):
	def __init__(self, thisScene, x, y):
		super().__init__(thisScene, "sprites/egg3.png", 128, 128, x, y)
	def update(self, offsetX, offsetY):
		super().update(offsetX, offsetY)
	def makeDecision(self):
		self.dy = 3
		self.timer = 120				

class GroundEnemy(BaseEnemy):
	def __init__(self, thisScene, x, y):
		super().__init__(thisScene, "sprites/snek.png", 100, 100, x, y)
		self.state = States.FALLING
	def update(self, offsetX, offsetY):
		super().update(offsetX, offsetY)
		if self.state == States.FALLING:
			if self.game.ground.collidesWith(self):
				self.state = States.STAND
				self.dy = 0	
	def makeDecision(self):
		self.timer = 100
		if self.state == States.STAND:
			decision = random.randint(0,1)
			if decision == 0:
				self.dx = random.randint(-2, 2)
			# if decision 1 run toward character
			if decision ==1:
				movementX = 0
				movementY = 0

				#find out if the main character is to the left of the enemy, if so move toward them - Kamille
				if self.game.main.posX < self.posX:
					movementX = -1

				# find out if the main character is to the right of the enemy, if so move toward them - Raphael
				if self.game.main.posX > self.posX:
					movementX = 1
				
				# move at random speed 
				self.dx = (random.randint(0,2) * movementX)				

class FlyingEnemy(BaseEnemy):
	def __init__(self, thisScene, x, y):
		super().__init__(thisScene, "sprites/birb.png", 100, 73, x, y)
	def update(self, offsetX, offsetY):
		super().update(offsetX, offsetY)
	def makeDecision(self):
		self.timer = 100
		decision = random.randint(0,1)	
		# decision 1, fly after main character
		if decision == 0:
			self.dx = random.randint(-3, 3)
			self.dy = random.randint(-3, 3)
		if decision ==1:
			movementX = 0
			movementY = 0		

			# find out if the main character is to the left of the enemy
			if self.game.main.posX < self.posX:
				movementX = -1		

			# find out if the main character is to the right of the enemy - Raphael
			if self.game.main.posX > self.posX:
				movementX = 1

			# find out if the main character is underneath the enemy (hint check y)	- sophie
			if self.game.main.posY < self.posY:
				movementY = -1

			# find out if the main character is above of the enemy - Kamille
			if self.game.main.posY > self.posY:
				movementY = 1	

			# move at random speed 
			self.dx = (random.randint(0,3) * movementX)
			self.dy = (random.randint(0,3) * movementY)


class Character(Spritesheet):
	# Constructor. Pass in the color of the block,
	# and its x and y position
	def __init__(self, game, sprite, x, y):
		# Call the parent class (Sprite) constructor
		super().__init__(game, sprite,x, y)
		self.stateTimer = 0
		self.dy = 7
		self.state = States.FALLING
		self.game = game
		

	def update(self, offsetX = 0, offsetY = 0):
		if self.state == States.FALLING:
			if self.game.ground.collidesWith(self):
				self.standBehavior()
		elif self.state == States.STAND or self.state == States.WALK:
			if self.game.keysDown[Keys.K_SPACE]:
				self.jumpBehavior()
			elif self.game.keysDown[Keys.K_RIGHT] or self.game.keysDown[Keys.K_LEFT]:
				self.walkBehavior()
			elif self.state == States.WALK:
				if (self.facing == Facing.RIGHT) and (self.game.keysDown[Keys.K_RIGHT] == False):
					self.standBehavior()
				if (self.facing == Facing.LEFT) and (self.game.keysDown[Keys.K_LEFT] == False):
					self.standBehavior()
		elif self.state == States.JUMP:
			self.stateTimer = self.stateTimer - 1
			if self.stateTimer < 1:
				self.dy = self.dy * -1
				self.state = States.FALLING
		super().update(offsetX, offsetY)		

	def standBehavior(self):
		self.dy = 0
		self.dx = 0
		self.state = States.STAND
		self.pauseAnimation()

	# override this in your Character
	def jumpBehavior(self):
		pass

	# override this in your Character
	def walkBehavior(self):
		pass

# sean mahady
#250x100
# 50, 50
class Sean(Character):
	def __init__(self, game):
		super().__init__(game, "sprites/sean_sheet.png", 500, 200)
		self.posX = 75	
		self.posY = 100
		self.loadAnimation(500, 200, 100, 100) 	# divides the sprite sheet into pieces
		self.setAnimationSpeed(10)	#sets a QTimer to 100ms
		self.playAnimation()	#starts the QTimer

		#make a state for you class
		self.state = States.FALLING	#falling

	# Add a method called walkBehavior. 
	# This should check if self.game.keysDown[Keys.kK_RIGHT]is True. If so self.facing to 0, self.setCurrentCycle to 0, call the self.playAnimation method. Set the DX to a value between 0 and 10. Set a State to States.WALK
	# If not check if self.game.keysDown[Keys.kK_LEFT] is True. If so self.facing to 1, self.setCurrentCycle to 1, call the self.playAnimation method. Set the DX to a value between 0 and -10. Set a State to States.WALK
	def walkBehavior(self):
		if self.game.keysDown[Keys.kK_RIGHT]:
			self.facing = 0
			self.setCurrentCycle(0)
			self.playAnimation()
			self.dx = 4
			self.state = States.WALK
		elif self.game.keysDown[Keys.kK_LEFT]:
			self.facing = 1
			self.setCurrentCycle(1)
			self.playAnimation()
			self.dx = -4
			self.state = States.WALK

	# Add a method called jumpBehavior. This should set the dy to a negative number (moving up), and set the stateTimer to the number of frames before falling.
	def jumpBehavior(self):
		self.stateTimer = 25
		self.dy = -4	
		self.state = States.JUMP



# newton's sprite
# 88x64
# 29x32
#Newton
class slimy(Character):
	def __init__(self, thisScene):
		super().__init__(thisScene, "sprites/newton_sheet.png",88,64)
		self.posX = 350
		self.posY = 200
		self.dy = 3
		self.loadAnimation(88, 64, 29, 32)
		self.setAnimationSpeed(10)
		self.playAnimation()
		self.state = States.FALLING
	def update(self, offsetX, offsetY):
		super().update(offsetX, offsetY)
		
	def walkBehavior(self):
		if self.game.keysDown[Keys.K_RIGHT]:
			self.facing = 0
			self.setCurrentCycle(0)
			self.playAnimation()
			self.dx = 7
			self.state = States.WALK
		elif self.game.keysDown[Keys.K_LEFT]:
			self.facing = 1
			self.setCurrentCycle(1)
			self.playAnimation()
			self.dx = -7
			self.state = States.WALK

	def jumpBehavior(self):
		self.stateTimer = 35
		self.dy = -7
		self.state = States.JUMP

# Animal
#Sheet 480 x 240
# Cell: 80x60
class IEATTERMITES(Character):
  def __init__(self,thisScene):
    super().__init__(thisScene, "sprites/niuniu_sheet.png", 480, 240)
    self.posX = 125
    self.posY = 180
    self.dy = 10

		# add loadAnimation, generateAnimation, setAnimationSpeed, and playAnimation methods
		#loadAnimation(sheetX, sheetY, cellX, cellY)
    self.loadAnimation(480, 240, 80, 60)
    self.setAnimationSpeed(30) #this is the highest number this will take
    self.playAnimation()  
  def update(self, offsetX, offsetY):
    super().update(offsetX, offsetY)


  def walkBehavior(self):
    if self.game.keysDown[Keys.K_RIGHT]:
      self.facing = 0
      self.setCurrentCycle(Facing.RIGHT)
      self.playAnimation()
      self.dx = 15
      self.state = States.WALK
    elif self.game.keysDown[Keys.K_LEFT]:
      self.facing = 1
      self.setCurrentCycle(2)
      self.playAnimation()
      self.dx = -15
      self.state = States.WALK

  def jumpBehavior(self):
    self.stateTimer = 30
    self.dy = -10
    self.state = States.JUMP		

# 112x173
# Jiayang
# Sheet: 484 x 346
# Cell: 96 x 173
class SQUID(Character):
	def __init__(self, thisScene):
		super().__init__(thisScene, "sprites/jiayang_sheet.png", 484, 346)
		self.posX = 150
		self.posY = 150
		self.dx = 4
		self.dy = 4


		# add loadAnimation, generateAnimation, setAnimationSpeed, and playAnimation methods
		self.loadAnimation(484, 346, 96, 173)
		self.setAnimationSpeed(30)
		self.playAnimation()
	def update(self, offsetX, offsetY):
		super().update(offsetX, offsetY)


	def walkBehavior(self):
		if self.game.keysDown[Keys.K_RIGHT]:
			self.facing = Facing.RIGHT
			self.setCurrentCycle(Facing.RIGHT)
			self.playAnimation()
			self.dx = 10
			self.state = States.WALK
		elif self.game.keysDown[Keys.K_LEFT]:
			self.facing = Facing.LEFT
			self.setCurrentCycle(Facing.LEFT)
			self.playAnimation()
			self.dx = -10
			self.state = States.WALK
	# Add a method called jumpBehavior. This should set the dy to a negative number (moving up), and set the stateTimer to the number of frames before falling.
	def jumpBehavior(self):
		self.dy = -10
		self.stateTimer = 33
		self.state = States.JUMP



    
 

# 400x144
# 100x72
# Tian
class MEEEEEE(Character):
	def __init__(self, thisScene):
		super().__init__(thisScene, "sprites/tian_sheet.png" , 400, 144)
		self.posX = 300
		self.posY = 30
		self.dy = 4
		self.loadAnimation(400, 144 , 100, 72)

		self.setAnimationSpeed(30)
		self.playAnimation()
		self.state = States.FALLING
	def update(self, offsetX, offsetY):
		super().update(offsetX, offsetY)

	def walkBehavior(self):
		if self.game.keysDown[Keys.k_RIGHT]:
			self.facing = 0
			self.setCurrentCycle(0)
			self.playAnimation()
			self.dx = 15
			self.state = States.WALK
		elif self.game.keysDown[Keys.k_LEFT]:
			self.facing = 1
			self.setCurrentCycle(1)
			self.playAnimation()
			self.dx = -15
			self.state = States.WALK
			
	def jumpBehavior(self):
		self.stateTimer = 26
		self.dy = -6	
		self.state = States.JUMP




class Window(Tk):
	def __init__(self, game):
		self.main = "None"
		super().__init__()
		self.game = game
		self.geometry('400x400')


		seanButton = Button(self, text="Sean", command=self.Sean)
		seanButton.pack()
		newtonButton = Button(self, text="Newton", command=self.Newton)
		newtonButton.pack()
		jiayangButton = Button(self, text="Jiayang", command=self.Jiayang)
		jiayangButton.pack()
		niuniuButton = Button(self, text="Niuniu", command=self.Niuniu)
		niuniuButton.pack()	
		tianButton = Button(self, text="Tian", command=self.Tian)
		tianButton.pack()	
							
		self.mainloop()

	def Sean(self):
		self.game.main = Sean(self.game)
		self.destroy()		

	def Newton(self):
		self.game.main = slimy(self.game)
		self.destroy()

	def Jiayang(self):
		self.game.main = SQUID(self.game)
		self.destroy()	

	def Niuniu(self):
		self.game.main = IEATTERMITES(self.game)
		self.destroy()		

	def Tian(self):
		self.game.main = MEEEEEE(self.game)
		self.destroy()	

				


class Game:
	def __init__(self):
		select = Window(self)

		if self.main == "None":
			raise ValueError('Selection Error.')
		
		pygame.init()

		# Setup the clock for a decent framerate
		self.clock = pygame.time.Clock()

		self.screen = pygame.display.set_mode((600, 600))

		self.camera = Camera(self)

		self.offsetX = 20
		self.offsetY = 20

		self.keysDown = [None] * 256

		self.bg0 = Background(self, "sprites/parallax-forest-back-trees.png", 1020, 600, .25, 0)
		self.bg1 = Background(self, "sprites/parallax-forest-middle-trees.png", 1020, 600, .5, 0)		
		self.bg2 = Background(self, "sprites/parallax-forest-front-trees.png", 1020, 600, .75, 0)
		self.bg3 = Background(self, "sprites/parallax-forest-lights.png", 1020, 600, 1, 0)		
		self.ground = Ground(self)

		



		self.spaceship = Spaceship(self)

		self.camera.follow(self.main)	

		self.sprites = pygame.sprite.Group()
		self.sprites.add(self.main)
		self.sprites.add(self.ground)
		self.sprites.add(self.spaceship)

		self.groundedSprites = pygame.sprite.Group()
		self.groundedSprites.add(self.main)

	# initializes key values to false
	def initKeys(self):
		for i in range(255):
			self.keysDown[i] = False
		for i in range(255):
			self.boardKeysDown[i] = False

	# check events
	def keyPressEvent(self, keys):
		if keys[pygame.K_LEFT]:
			self.keysDown[Keys.K_LEFT] = True
		else:
			self.keysDown[Keys.K_LEFT] = False

		if keys[pygame.K_RIGHT]:
			self.keysDown[Keys.K_RIGHT] = True
		else:
			self.keysDown[Keys.K_RIGHT] = False	

		if keys[pygame.K_SPACE]:
			self.keysDown[Keys.K_SPACE] = True
		else:
			self.keysDown[Keys.K_SPACE] = False


	# execute our main loop
	def run(self):
		done = False

		while not done:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					done = True


			keys = pygame.key.get_pressed()  #checking pressed keys
			self.keyPressEvent(keys)

			# Add this somewhere after the event pumping and before the display.flip()
			pygame.draw.rect(self.screen, (0, 128, 255), pygame.Rect(30, 30, 60, 60))

			self.bg0.draw(self.offsetX, self.offsetY)
			self.bg1.draw(self.offsetX, self.offsetY)
			self.bg2.draw(self.offsetX, self.offsetY)
			self.bg3.draw(self.offsetX, self.offsetY)







			for sprite in self.sprites:
				sprite.update(self.offsetX, self.offsetY)

			self.camera.update()




			self.sprites.draw(self.screen)

			for enemy in self.spaceship.enemies:
				if pygame.sprite.collide_circle_ratio(0.4)(enemy,self.main):
					print("You died!")
					done = True
       
			pygame.display.flip()

			self.clock.tick(30)

game = Game()
game.run()