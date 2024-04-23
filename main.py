"""
Tetris Bot
Joseph Reiner
Slippery Rock University
CPSC 476 - Artificial Intelligence
"""

from tetris import *
import sys
import copy
import bot
	
def gameLoop():		
	"""Main loop that runs the game."""

	blockSize = 20 
	boardColNum = 10 
	boardRowNum = 20
	boardLineWidth = 10
	blockLineWidth = 1
	scoreBoardWidth = blockSize * (boardColNum//2)
	boardPosX = DISPLAY_WIDTH*0.3
	boardPosY = DISPLAY_HEIGHT*0.15

	mainBoard = MainBoard(blockSize,boardPosX,boardPosY,boardColNum,boardRowNum,boardLineWidth,blockLineWidth,scoreBoardWidth)	
	
	tBot = bot.Bot()
	
	gameSpeed = 600
	
	gameExit = False

	while not gameExit: #Stay in this loop unless the game is quit
		
		for event in pygame.event.get():	
			if event.type == pygame.QUIT: #Looks for quitting event in every iteration (Meaning closing the game window)
				gameExit = True
				
			if event.type == pygame.KEYDOWN: #Keyboard keys press events
				if event.key == pygame.K_p:
					if key.pause.status == 'idle':
						key.pause.trig = True
						key.pause.status = 'pressed'
				if event.key == pygame.K_r:
					if key.restart.status == 'idle':
						key.restart.trig = True
						key.restart.status = 'pressed'
				if event.key == pygame.K_RETURN:
					key.enter.status = 'pressed'
						
			if event.type == pygame.KEYUP: #Keyboard keys release events
				if event.key == pygame.K_p:
					key.pause.status = 'idle'
				if event.key == pygame.K_r:
					key.restart.status = 'idle'
				if event.key == pygame.K_RETURN:
					key.enter.status = 'idle'
			
		
		gameDisplay.fill(BLACK) #Whole screen is painted black in every iteration before any other drawings occur 
			
		mainBoard.gameAction() #Apply all the game actions here	
		mainBoard.draw() #Draw the new board after game the new game actions
		gameClock.update() #Increment the frame tick

		tBot.update(copy.deepcopy(mainBoard.blockMat), mainBoard.piece, mainBoard.nextPieces, mainBoard.gameStatus, key)
		
		if mainBoard.piece.status == "moving" and runCount == 0:
			tBot.run()
			runCount = 1
		if mainBoard.piece.status == "uncreated":
			runCount = 0
		else:
			tBot.movement(mainBoard.piece)

		if mainBoard.score != 0:
			tBot.drawBoard(gameDisplay) # draw mini board with bot analysis

		pygame.display.update() #Pygame display update
		clock.tick(gameSpeed) #Pygame clock tick function (default is 60 fps)

pygame.display.set_caption('Tetris')
gameLoop()	
pygame.quit()
sys.exit()