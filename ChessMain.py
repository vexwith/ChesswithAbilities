"""
main driver file. It will be responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
import math as m
from chess import ChessEngine, SmartMoveFinder
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512 #or 400
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8 #dimensions of a chess board are 8x8
SQ_SIZE = BOARD_WIDTH // DIMENSION
MAX_FPS = 15 #for animations later on
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''
def loadImages():
    pieces = ['wP', 'wR', 'wB', 'wN', 'wK', 'wQ', 'bP', 'bR', 'bB', 'bN', 'bK', 'bQ', 'Okonogi', 'Kanon', 'Shanon',
              'Kraus', 'Shanon-furniture', 'Akasaka']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE , SQ_SIZE))
    #we can now acces an image by saying "IMAGES['wP']" for example

'''
the main driver for our code. This will handle user input and updating the graphisc
'''
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 20, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    validOrders = gs.getAllPossibleOrders()
    moveMade = False #flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    loadImages() #we do it only once, before the while loop
    running = True
    sqSelected = () #no square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = [] #keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    sqSelectedO = () #the same but for Order
    playerClicksO = [] #keep tracks of player clicks (we will need 2)
    gameOver = False
    playerOne = True #if a Human is playing white, then this will be true and false if AI is playing
    playerTwo = True #the same as above but for black
    AIThinking = False #if AI is thinking of a move so that we can still do things
    moveFinderProcess = None #the process of thinking is done here
    moveUndone = False #AI cant move while moveUndone
    showSpritesPress = False #flag variable for showing sprites by pressing once
    startingPhase = False #flag variable signifying starting phase
    while running:
        humanTurn = (gs.WhiteToMove and playerOne) or (not gs.WhiteToMove and playerTwo) #can play only when its human turn
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if startingPhase:
                    if e.button == 1: #mouse left click
                        if not gameOver:
                            location = p.mouse.get_pos() #(x, y) location of mouse
                            col = location[0]//SQ_SIZE
                            row = location[1]//SQ_SIZE
                            if sqSelected == (row, col) or col >= 8: #user clicked the same square or user clicked the move log
                                sqSelected = () #deselect
                                playerClicks = [] #clear player clicks
                            else:
                                sqSelected = (row, col)
                                #playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                            if len(playerClicks) == 2 and humanTurn: #after 2nd click
                                move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        #print(move.getChessNotation(gs.board))
                                        gs.makeMove(validMoves[i])
                                        moveMade = True
                                        animate = True
                                        sqSelected = ()
                                        playerClicks = [] #reset user clicks
                                if not moveMade:
                                    playerClicks = [sqSelected] #if you clicked on your different piece
                if not startingPhase:
                    if e.button == 1: #mouse left click
                        if not gameOver:
                            location = p.mouse.get_pos() #(x, y) location of mouse
                            col = location[0]//SQ_SIZE
                            row = location[1]//SQ_SIZE
                            if sqSelected == (row, col) or col >= 8: #user clicked the same square or user clicked the move log
                                sqSelected = () #deselect
                                playerClicks = [] #clear player clicks
                            else:
                                sqSelected = (row, col)
                                playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                            if len(playerClicks) == 2 and humanTurn: #after 2nd click
                                move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        #print(move.getChessNotation(gs.board))
                                        gs.makeMove(validMoves[i])
                                        moveMade = True
                                        animate = True
                                        sqSelected = ()
                                        playerClicks = [] #reset user clicks
                                if not moveMade:
                                    playerClicks = [sqSelected] #if you clicked on your different piece
                    if e.button == 3: #mouse right click
                        if not gameOver:
                            locationO = p.mouse.get_pos() #(x, y) location of mouse for Order
                            colO = locationO[0]//SQ_SIZE
                            rowO = locationO[1]//SQ_SIZE
                            if sqSelectedO == (rowO, colO) or colO >= 8: #user clicked the same square or user clicked the move log
                                sqSelectedO = () #deselect
                                playerClicksO = []
                            else:
                                sqSelectedO = (rowO, colO)
                                playerClicksO.append(sqSelectedO)
                            if len(playerClicksO) == 2 and humanTurn:
                                name = gs.board[playerClicksO[0][0]][playerClicksO[0][1]][3:]
                                order = ChessEngine.Order(playerClicksO[0], playerClicksO[1], gs.board, name)
                                for o in range(len(validOrders)):
                                    if order == validOrders[o]:
                                        gs.placeOrder(validOrders[o])
                                        moveMade = True
                                        sqSelectedO = ()
                                        playerClicksO = [] #reseting clicks
                                    if not moveMade:
                                        playerClicksO = [sqSelectedO]


            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

                if e.key == p.K_r: #reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_x: #show sprites by pressing once
                    showSpritesPress = not showSpritesPress
        #key holding handlers
        keys = p.key.get_pressed()  # checking pressed keys
        if keys[p.K_LCTRL]:
            showSprites = not showSpritesPress #flag variable to show sprites instead of pieces
        else:
            showSprites = showSpritesPress

        #AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue() #used to pass data between threads
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start() #call findBestMove(gs, validMoves, returnQueue)

            if not moveFinderProcess.is_alive():
                print("done thinking")
                AIMove = returnQueue.get()
                if AIMove is None: #We dont really need that
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
                if len(gs.moveLog) > 0:
                    print(gs.moveLog[-1].getChessNotation())
            validMoves = gs.getValidMoves()
            validOrders = gs.getAllPossibleOrders()
            moveMade = False
            animate = False
            moveUndone = False
            sqSelected = ()
            playerClicks = []
            sqSelectedO = ()
            playerClicksO = []

        drawGameState(screen, gs, validMoves, sqSelected, validOrders, sqSelectedO, moveLogFont, showSprites)

        #ending the game, disabling any more moves
        if len(validMoves) == 0:
            gameOver = True
            #drawing the end game text
            if gs.inCheck:
                #simplifying the logic
                text = 'Black wins by checkmate' if gs.WhiteToMove else 'White wins by checkmate'
            else:
                text = 'Stalemate'
            drawEndGameText(screen, text)


        clock.tick(MAX_FPS)
        p.display.flip()


'''
Responsible for all the graphics within a currrent game state
'''
def drawGameState(screen, gs, validMoves, sqSelected, validOrders, sqSelectedO, moveLogFont, showSprites):
    drawBoard(screen) #draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected, validOrders, sqSelectedO)
    drawPieces(screen, gs.board, showSprites) #draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)

'''
draw the squares on the board
'''
def drawBoard(screen):
    global colors
    colors = [p.Color(235, 210, 175), p.Color(176, 126, 91)] #235, 210, 175 ; 176, 126, 91
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)] #changing color if its an odd or even square
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected, validOrders, sqSelectedO):
    if sqSelectedO != ():
        rO, cO = sqSelectedO
        if gs.board[rO][cO][0] == ('w' if gs.WhiteToMove else 'b'): #if sqSelectedO has an order that can be used
            #highlighting selected square
            sO = p.Surface((SQ_SIZE, SQ_SIZE))
            sO.set_alpha(150) #transperancy value -> 0 transparent; 255 opaque
            #highlight moves from that square
            sO.fill(p.Color(96, 96, 96))
            for order in validOrders:
                if order.startRow == rO and order.startCol == cO:
                    '''
                    if order.targetPiece == '--':
                        screen.blit(sO, (order.endCol*SQ_SIZE, order.endRow*SQ_SIZE))
                    else:
                    '''
                    screen.blit(sO, (order.endCol * SQ_SIZE, order.endRow * SQ_SIZE))
                    p.draw.rect(screen, 'green', p.Rect(order.endCol * SQ_SIZE, order.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.WhiteToMove else 'b'): #checking if sqSelected is a piece that can be moved
            #highlighting selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150) #transperancy value -> 0 transparent; 255 opaque
            s.fill(p.Color(96, 96, 96))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            p.draw.rect(screen, 'yellow', p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)
            #highlight moves from that square
            s.fill(p.Color(96, 96, 96))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if move.pieceCaptured == '--' and not move.isEnpassantMove:
                        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
                    else:
                        screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
                        p.draw.rect(screen, 'yellow', p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)

    if gs.shanonFurnitureBarrierStatus > 1:
        b = p.Surface((SQ_SIZE * 2, SQ_SIZE * 2))
        b.set_alpha(100)  # transperancy value -> 0 transparent; 255 opaque
        b.fill(p.Color("red"))
        sFBC = gs.shanonFurnitureBarrierCords[0]
        #print(sFBC)
        screen.blit(b, (sFBC[1] * SQ_SIZE, sFBC[0] * SQ_SIZE))
        p.draw.rect(screen, 'red', p.Rect(sFBC[1] * SQ_SIZE, sFBC[0] * SQ_SIZE, SQ_SIZE * 2, SQ_SIZE * 2), 4)


'''
draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board, showSprites=False):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            if showSprites and len(board[r][c]) > 4 and board[r][c][:-2] != '--':
                if board[r][c][-2:] == 'xx':
                    piece = board[r][c][3:-2]
                else:
                    piece = board[r][c][3:]
            else:
                piece = board[r][c][0:2]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draws the move log
'''
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLogProp
    moveTexts = []
    for i in range(0, len(moveLog), 2): #going by 2 from 0 to one less than len(moveLog)
        moveStr = str(i//2 + 1) + ". " + moveLog[i].getChessNotation() + " "
        if i+1 < len(moveLog): #make sure black made a move
            moveStr += moveLog[i+1].getChessNotation() + "    " #updating the string above by adding next move too
        moveTexts.append(moveStr)

    movesPerRow = 2
    padding = 5
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        #algorithm to establish how many moves are shown in a row
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, False, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height()

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square
    squaresToMove = int(m.sqrt((pow(abs(dR), 2) + pow(abs(dC), 2)))) #the amount of squares piece goes, i used pitagoras here for vertical movement
    frameCount = squaresToMove * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw the captured piece onto rectangle
        if move.pieceCaptured != '--' and move.pieceCaptured != '--xx':
            screen.blit(IMAGES[move.pieceCaptured[0:2]], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved[0:2]], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(120*(squaresToMove/2)) #frames per second, theyr higher the further square you go

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, False, p.Color('purple'))
    #centering the text
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color('black')) #adding shadow
    screen.blit(textObject, textLocation.move(-2, 2))

if __name__ == "__main__":
    main()





















