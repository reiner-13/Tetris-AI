from tetris import *
import sys
import copy
import bot
import pygad

def gameLoop(solution):		
	"""
	Main loop that runs game.
	Returns score as fitness to GA.
	"""
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
	tBot.setWeights(solution)
	
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

		if mainBoard.gameStatus == "gameOver":
			key.enter.status = 'pressed'
			return mainBoard.score


		pygame.display.update() #Pygame display update
		clock.tick(gameSpeed) #Pygame clock tick function(60 fps)
		

def fitness_func(ga_instance, solution, solution_idx):
	score = gameLoop(solution)
	return score

def on_gen(ga_instance):
	print("Generation: ", ga_instance.generations_completed)
	print("Fitness of best solution: ", ga_instance.best_solution())


function_inputs = [1, 1, 1, -1]

num_generations = 100
num_parents_mating = 5

sol_per_pop = 10
num_genes = len(function_inputs)

init_range_low = 0
init_range_high = 1

parent_selection_type = "sss"
keep_parents = 1

crossover_type = "single_point"
mutation_type = "random"
mutation_probability = 0.005

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       init_range_low=init_range_low,
                       init_range_high=init_range_high,
                       parent_selection_type=parent_selection_type,
                       crossover_type=crossover_type,
                       mutation_type=mutation_type,
                       mutation_probability=mutation_probability,
                       on_generation=on_gen)

ga_instance.run()

solution, solution_fitness, solution_idx = ga_instance.best_solution()
print("Parameters of the best solution : {solution}".format(solution=solution))
print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))


pygame.quit()
sys.exit()