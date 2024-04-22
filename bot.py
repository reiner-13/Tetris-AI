import pygame #version 2.5.2
import copy
import numpy as np
import matplotlib.image

class TreeNode:
	"""
	Class for the nodes in the decision search tree.
	Holds values about the associated positions.
	"""
	def __init__(self, data):
		self.data = data
		self.parent = None
		self.children = []
		self.evaluation = 0
		self.coords = [0,0]
		self.avgColumnHeight = 0
		self.bumpiness = 0
		self.holes = 0
		self.lines = 0
		self.orientation = 0

class Bot:
	"""
	Creates a search tree to view all possible moves
	and determines which is most advantageous based off
	evaluation.\n
	Moves the current piece into target position.
	"""
	def __init__(self):
		self.boardArr = None # current board layout in a numpy 2d array
		self.colorMap = matplotlib.colors.LinearSegmentedColormap.from_list("custom", ["#333333", "#cc2222", "#006600", "#087700", "#108800", "#189900", "#20aa00", "#28bb00", "#30cc00", "#38dd00", "#40ff00"])
		self.checkedPositions = [] # list of numpy 2d arrays
		self.targetPosition = [0,0]
		self.searchTree = None
		self.bestNode = TreeNode(None)
		self.orientation = 0
		self.key = None

		self.avgHeightWeight = 1.392
		self.bumpinessWeight = 0.861
		self.holesWeight = 4.540
		self.lineWeight = -0.193

	
	def setWeights(self, weights : list):
		"""Sets bot weights in order of avgHeight, bumpiness, holes, lines."""
		self.avgHeightWeight = weights[0]
		self.bumpinessWeight = weights[1]
		self.holesWeight = weights[2]
		self.lineWeight = weights[3]
		

	def update(self, blockMat, movingPiece, nextPieces, gameStatus, key):
		"""
		Updates various data every frame.
		To do this, it takes in a MainBoard's blockMat, movingPiece, nextPieces, gameStatus, and key.
		"""
		for i in range(len(blockMat)):
			for j in range(len(blockMat[i])):
				if blockMat[i][j] == "empty":
					blockMat[i][j] = 0
				else:
					blockMat[i][j] = 1
		
		self.boardArr = np.array(blockMat)
		self.movingPiece = movingPiece
		self.nextPieces = nextPieces # nextPieces[0] is current piece, nextPieces[1] is next piece
		self.gameStatus = gameStatus
		self.key = key
		self.maxTreeDepth = len(nextPieces) # 2

	
	def run(self):
		"""Called every time a new block appears."""
		if self.gameStatus == 'running':
			self.nextPiece = copy.deepcopy(self.movingPiece)
			self.nextPiece.type = self.nextPieces[1]
			self.nextPiece.spawn()
			self.orientation = 0

			# Create the search tree and choose the position leading to the best outcome
			self.createTree(None, 0)
			self.bestNode = self.chooseBest()
			if self.bestNode.parent != None:
				self.bestNode = self.bestNode.parent
					
			# Update the target position for movement and nullify the search tree for the next call
			self.targetPosition = self.bestNode.coords
			self.searchTree = None

			# Updates mini-board
			self.boardArr[self.bestNode.coords[0]][self.bestNode.coords[1]] = 10
			matplotlib.image.imsave('images/board.png', self.boardArr, cmap=self.colorMap)

	
	def movement(self, movingPiece):
		"""Moves the current piece given the target position."""
		
		# Rotate piece if necessary
		while self.orientation != self.bestNode.orientation:
			self.orientation += 1
			if self.bestNode.coords[1] < 5 and movingPiece.type == 'I':
				movingPiece.rotate('cCW')
			else:
				movingPiece.rotate('CW')
		
		# Find leftmost block in current piece
		cols = []
		for block in movingPiece.blocks:
			cols.append(block.currentPos.col)
		leftmostBlockCol = cols.index(min(cols))
		
		# Movement
		if self.key.down.status == 'pressed':
			self.key.down.status = 'released'
		if movingPiece.blocks[leftmostBlockCol].currentPos.col < self.targetPosition[1]:
			self.key.xNav.status = 'right'
		elif movingPiece.blocks[leftmostBlockCol].currentPos.col > self.targetPosition[1]:
			self.key.xNav.status = 'left'
		else:
			# Slow down in certain cases, otherwise hold down
			if self.bestNode.avgColumnHeight > 12 or (max(self.getColumnHeights(self.bestNode.data)) > 10 and movingPiece.type == 'I' and self.orientation == 1 and self.bestNode.coords[1] <= 1): # eyeballed values
				self.key.xNav.status = 'idle'
			else:
				self.key.xNav.status = 'idle'
				self.key.down.status = 'pressed'
	
	
	def getColumnHeights(self, data):
		"""Returns a list of the column heights of the given board."""
		heights = []
		# want to iterate through columns, so we transpose the data array
		for row in np.transpose(data):
			count = 0
			for cell in row:
				if cell == 0:
					count += 1
				else:
					break
			heights.append(20 - count)
			
		return heights

	
	def createTree(self, root, depth):
		"""Creates the tree of positions recursively. First creates depth 0, then depth 1."""
		
		if depth == 2:
			return
		# Assigns the current root (newRoot)
		if depth == 0:
			newRoot = TreeNode(self.boardArr)
			currentPiece = self.movingPiece
		else:
			newRoot = root
			currentPiece = self.nextPiece

		self.createNodes(newRoot, currentPiece)

		# Forms self.searchTree
		for childNode in newRoot.children:
			self.createTree(childNode, depth+1)
		
		self.searchTree = newRoot
	
	
	def createNodes(self, root, currentPiece):
		"""Feeds piece and board state at hand into generatePosition() in all orientations."""

		# Find orientation count given type of piece
		orientations = 0
		if self.movingPiece.type == 'O':
			orientations = 1
		elif self.movingPiece.type == 'S' or self.movingPiece.type == 'Z' or self.movingPiece.type == 'I':
			orientations = 2
		else:
			orientations = 4
		
		# Get list of target positions for piece at hand
		targetPositions = []
		orientationMap = {}
		for orientation in range(orientations):
			newPositions = self.generatePosition(root, currentPiece)
			targetPositions += newPositions
			orientationMap[len(targetPositions) - len(newPositions)] = [orientation, copy.deepcopy(currentPiece.currentDef)]
			currentPiece.rotate('CW')

		# Create nodes
		mappedOrientation = 0
		currentKey = 0
		for i, tar in enumerate(targetPositions):
			if i in orientationMap.keys():
				mappedOrientation = orientationMap[i][0]
				currentKey = i

			newNodeData = copy.deepcopy(root.data)
			for pos in orientationMap[currentKey][1]:
				if tar in targetPositions:
					newNodeData[tar[0] + pos[0]][tar[1] + pos[1]] = 1

			newNode = TreeNode(newNodeData)
			newNode.coords = tar
			newNode.orientation = mappedOrientation
			newNode.evaluation = self.objFunc(newNode)
			root.children.append(newNode)
			newNode.parent = root

		
	
	def generatePosition(self, root, currentPiece):
		"""Generates all possible positions given the piece and board state at hand."""
		
		targetPositions = []
		defPositions = currentPiece.currentDef
		defRows = [x[0] for x in defPositions]
		defCols = [x[1] for x in defPositions]
		# if there's a gap in row 0 of definition
		while 0 not in defRows:
			for pos in defPositions:
				pos[0] -= 1
			defRows = [x[0] for x in defPositions]
		# if there's a gap in column 0 of definition
		while 0 not in defCols:
			for pos in defPositions:
				pos[1] -= 1
			defCols = [x[1] for x in defPositions]
		colCount = 10 - max(defCols)
		
		
		for j in range(colCount):
			for i in range(20):
				target = False
				startPos = (i, j)

				for pos in defPositions:
					if startPos[0] + pos[0] >= 20:
						target = True
						targetPositions.append([i-1, j])
						break
					if startPos[1] + pos[1] >= 10:
						target = True
						targetPositions.append([i, j-1])
					if root.data[startPos[0] + pos[0]][startPos[1] + pos[1]] == 0:
						continue
					else:
						target = True
						targetPositions.append([i-1, j]) # previous start position
						break
				
				if target:
					break

		return targetPositions
	
	
	def chooseBest(self):
		"""Chooses the best node in depth 2 of self.searchTree."""
		bestEvaluation = 10000
		bestChild = TreeNode(None)

		for child in self.searchTree.children:
			for grandchild in child.children:
				if grandchild.evaluation < bestEvaluation:
					bestEvaluation = grandchild.evaluation
					bestChild = grandchild
		
		return bestChild

	
	def objFunc(self, node : TreeNode):
		"""
		Evaluates a given node by assigning a score based on the following metrics:
		line completion, average height, bumpiness, and hole count.
		"""

		# LINE COMPLETION
		lineCount = 0
		for i, row in enumerate(node.data):
			if all(j == 1 for j in row):
				lineCount += 1
				node.data = np.delete(node.data, i, 0)
				node.data = np.insert(node.data, 0, np.array((0,0,0,0,0,0,0,0,0,0)), 0) # removes lines
		if lineCount == 2:
			lineCount = 2.5
		elif lineCount == 3:
			lineCount = 7.5
		elif lineCount == 4:
			lineCount = 30
		node.lines = lineCount

		# AVERAGE HEIGHT
		self.columnHeights = self.getColumnHeights(node.data)
		node.avgColumnHeight = sum(self.columnHeights) / len(self.columnHeights)

		# BUMPINESS
		for i in range(len(self.columnHeights) - 1):
			node.bumpiness += abs(self.columnHeights[i] - self.columnHeights[i+1])

		# HOLES
		holeCount = 0
		holeCounting = False
		for row in np.transpose(node.data):
			for val in row:
				if val == 0 and not holeCounting:
					continue
				if val != 0:
					holeCounting = True
				if val == 0 and holeCounting:
					holeCount += 1
			holeCounting = False
		
		node.holes = holeCount

		return node.avgColumnHeight*self.avgHeightWeight + node.bumpiness*self.bumpinessWeight + node.holes*self.holesWeight + node.lines*self.lineWeight

	
	def drawBoard(self, gameDisplay):
		"""Draws a simplified board, which shows the target position for the current piece."""
		boardImage = pygame.image.load("images/board.png")
		boardImage = pygame.transform.scale(boardImage, [100,200])
		gameDisplay.blit(boardImage, [680, 380])
