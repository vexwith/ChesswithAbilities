"""
This class is responsible for storing the information about the current state of a chess game. It will also be
responsible for determining the valid moves at the current state. It will also keep a move log.
"""

import copy

class GameState():
    def __init__(self):
        #board is an 8x8 2 dimensional list, each element of the list has 2 characters.
        #the first character represents the color of the piece, 'b' or 'w'
        #the second character represents the type of piece, 'K', 'Q', 'R', 'B', 'N', or 'P'
        # "--" represents an empty space without any piece

        '''
        self.board = [
            ["--", "--", "--", "--", "bK", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "wK", "--", "--", "--"]]
        '''
        self.board = [
            ["bR_Kanon", "bN", "bB", "bQ", "bK", "bB", "bN", "bR_Shanon"],
            ["bP", "bP", "bP", "bP_Okonogi", "bP_Kraus", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP_Kraus", "wP_Okonogi", "wP", "wP", "wP"],
            ["wR_Kanon", "wN_Shanon-furniture", "wB", "wQ_Akasaka", "wK", "wB", "wN", "wR_Shanon"]]
        '''
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN_Shanon-furniture", "wB", "wQ_Akasaka", "wK", "wB", "wN", "wR"]]
        '''

        #here we store starting phase information
        self.whiteHand = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR",
                          "bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"]
        self.blackHand = ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP",
                          "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        self.allowedPlaces = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunction = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.abilitiesFunction = {'Okonogi': self.Okonogi, 'Kanon': self.Kanon, 'Shanon': self.Shanon,
                                  'Kraus': self.Kraus, 'Shanon-furniture': self.ShanonFurniture, 'Akasaka': self.Akasaka}
        self.ordersFunction = {'Kraus': self.krausOrder, 'Shanon-furniture': self.shanonFurnitureOrder}

        self.WhiteToMove = True
        self.moveLog = []
        self.moveLogProp = []

        #variables concerning orders
        self.orderPlaced = False #flag variable to figure out if order was made and allow to execute it
        #we will keep track of when order is activated and switch it to false, so it cannot be used again
        self.ordersAccess = {'Krausw': True, 'Krausb': True, 'Shanon-furniturew': True, 'Shanon-furnitureb': True}
        self.undoOrder = False #flag variable for undoing moves

        #variables concerning checking and pinning
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = [] #coordinates of a pinned piece
        self.checks = [] #coordinates of a checking piece

        #enpassant variables
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]

        #castling variables
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                            self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]
        #Kanon - Rook variables
        self.currentKanonRook = [] #saving coordinates of threatened pieces both for white and black
        self.currentKanonRookNr = None #the number of package from currentKanonRook
        self.KanonRookSpecialMoveLog = []
        self.KanonRookPermission = False

        #Shanon - Rook variables
        self.currentShanonRook = [] #same as Kanon
        self.currentShanonRookNr = None
        self.ShanonRookPermission = False

        #Shanon - furniture - knight variables
        self.shanonFurnitureBarrierStatus = 0
        self.shanonFurnitureBarrierCords = []


    '''
    Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion and en-passant, etc)
    '''
    def makeMove(self, move):
        if self.board[move.startRow][move.startCol][:-2] == "xx":
            self.board[move.startRow][move.startCol] = "--xx"
        else:
            self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.moveLogProp.append(move) #logging the move (without orders) for the drawMoveLog function in ChessMain
        self.WhiteToMove = not self.WhiteToMove #swap players
        #update king's location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            global promotedPiece
            promotedPiece = 'Q' #input("Promote to Q, R, B or N:") #we can make this part of the ui later
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" #capturing the pawn after enpassanting

        #update enpassantPossible variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        self.enpassantPossibleLog.append(self.enpassantPossible)

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves the rook
                self.board[move.endRow][move.endCol+1] = '--' #erase old rook
            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #moves the rook
                self.board[move.endRow][move.endCol-2] = '--'  # erase old rook

        #update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

        #kanon - Rook special move access
        if len(self.currentKanonRook) > 0:
            for krsm in range(len(self.currentKanonRook)):
                color = self.currentKanonRook[krsm].allyColor
                if (color == 'w' and self.WhiteToMove) or (color == 'b' and not self.WhiteToMove):
                    self.KanonRookPermission = True #after opponent makes a move and kanon was threatening someone
                    # last turn then the permission + package and package number will be sent to Kanon ability function
                    self.currentKanonRookNr = krsm
                    break

        #shanon - Rook special move access
        if len(self.currentShanonRook) > 0:
            for srsm in range(len(self.currentShanonRook)):
                color = self.currentShanonRook[srsm].allyColor
                if (color == 'w' and self.WhiteToMove) or (color == 'b' and not self.WhiteToMove):
                    self.ShanonRookPermission = True #after opponent makes a move and shanon was protecting someone
                    # last turn then the permission + package and package number will be sent to Shanon ability function
                    self.currentShanonRookNr = srsm
                    break

        #shanon - furniture barrier countdown
        if self.shanonFurnitureBarrierStatus == 1:
            self.shanonFurnitureBarrierStatus = 0
            for x in range(4):
                cords = self.shanonFurnitureBarrierCords.pop()
                self.board[cords[0]][cords[1]] = self.board[cords[0]][cords[1]][:-2]
                print(self.board[cords[0]][cords[1]])
        if self.shanonFurnitureBarrierStatus > 1:
            self.shanonFurnitureBarrierStatus -= 1

    '''
    Undo the last move done
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            move = self.moveLog.pop()
            if len(str(move.moveID)) == 4: #if its a Move
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured
                self.WhiteToMove = not self.WhiteToMove #switch turns back
                # update king's location
                if move.pieceMoved == "wK":
                    self.whiteKingLocation = (move.startRow, move.startCol)
                elif move.pieceMoved == "bK":
                    self.blackKingLocation = (move.startRow, move.startCol)

                #undo en passant
                if move.isEnpassantMove:
                    #gives the captured piece back
                    if self.WhiteToMove:
                        self.board[move.startRow][move.endCol] = 'bP'
                    else:
                        self.board[move.startRow][move.endCol] = 'wP'
                #reestablishing the enpassant move
                self.enpassantPossibleLog.pop()
                self.enpassantPossible = self.enpassantPossibleLog[-1]

                #undo castling rights
                self.castleRightLog.pop() #get rid of the latest castle rights
                self.currentCastlingRights = copy.deepcopy(self.castleRightLog[-1]) #set the current castling rights to the last one in the list
                #undo the castle move
                if move.isCastleMove:
                    if move.endCol - move.startCol == 2: #kingside
                        self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1] #putting the rook back
                        self.board[move.endRow][move.endCol-1] = '--'
                    else: #queenside
                        self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1] #putting the rook back
                        self.board[move.endRow][move.endCol+1] = '--'

                #undo kanon - rook special move
                if len(self.KanonRookSpecialMoveLog) > 0:
                    draftKanonRook = self.KanonRookSpecialMoveLog.pop()
                    if draftKanonRook != 0:
                        self.KanonRookPermission = True
                        self.currentKanonRookNr = -1
                        self.currentKanonRook.append(draftKanonRook)
                    print(self.KanonRookSpecialMoveLog)

                self.moveLogProp.pop()

            elif len(str(move.moveID)) > 4: #if its an Order
                self.undoOrder = True
                self.ordersFunction[move.name](move.startRow, move.startCol, None)



    '''
    Takes order as a parameter and sends it to function that will execute it
    '''
    def placeOrder(self, order):
        self.orderPlaced = True
        self.ordersFunction[order.name](order.startRow, order.startCol, order)
        self.moveLog.append(order)


    '''
    Update the castle rights given the move
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.bks = False
        elif move.pieceCaptured == 'wR': #if rook got captured
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.WhiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                #to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #enemy piece causing the check
                validSquares = [] #squares that pieces can move to
                #if knight player must capture knight or move king
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once you get to piece end checks
                            break
                #get rid of any moves that dont block check or move king
                for i in range(len(moves) - 1, -1, -1): #go trough the list backwards when youre removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K': #move doesnt move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesnt block check or capture piece
                            moves.remove(moves[i])
            else: #double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #not in check so all moves are fine
            moves = self.getAllPossibleMoves()


        return moves

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in a given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.WhiteToMove) or (turn == 'b' and not self.WhiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves) #calls the appropriate move function based on piece type
                    if len(self.board[r][c]) > 4 and self.board[r][c][:-2] != '--':
                        if self.board[r][c][-2:] == 'xx':
                            pieceAbility = self.board[r][c][3:-2]
                        else:
                            pieceAbility = self.board[r][c][3:]
                        self.abilitiesFunction[pieceAbility](r, c, moves) #calls the appropriate ability function based on piece type
        return moves

    '''
    All moves without considering checks
    '''

    def getAllPossibleOrders(self):
        orders = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of cols in a given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.WhiteToMove) or (turn == 'b' and not self.WhiteToMove):
                    if len(self.board[r][c]) > 2:
                        piece = self.board[r][c][3:]
                        if piece in self.ordersFunction:
                            self.ordersFunction[piece](r, c, orders) #calls the appropriate order function based on piece
        return orders

    '''
    Get all the pawn moves for the pawn located at row, col and add those moves to the list
    '''
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c: #checking if this piece is being pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i]) #removing the pin from pins for efficiency
                break

        if self.WhiteToMove:
            moveDirection = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveDirection = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation
        pawnPromotion = False #flag variable

        block = True if self.board[r][c][-2:] == 'xx' else False #'xx' pieces are unable to move out of xx

        if (self.board[r+moveDirection][c] == "--" and not block) or (self.board[r+moveDirection][c] == "--xx" and block): #1 square pawn advance
            #print(self.board[r+moveDirection][c])
            if not piecePinned or pinDirection == (moveDirection, 0): #pawn can move only when not pinned or if the direction matches
                if r+moveDirection == backRow: #if piece gets to bank rank then it is a pawn promotion
                    pawnPromotion = True
                moves.append(Move((r, c), (r+moveDirection, c), self.board, isPawnPromotion=pawnPromotion))
                if r == startRow and self.board[r+2*moveDirection][c] == "--": #2 square pawn advance
                    moves.append(Move((r, c), (r+2*moveDirection, c), self.board))
        if c-1 >= 0: #captures to the left
            if not piecePinned or pinDirection == (moveDirection, -1):
                if (self.board[r + moveDirection][c - 1][-2:] != 'xx' and not block) or (self.board[r + moveDirection][c - 1][-2:] == 'xx' and block):
                    if self.board[r+moveDirection][c-1][0] == enemyColor: #enemy piece to capture
                        if r+moveDirection == backRow:
                            pawnPromotion = True
                        moves.append(Move((r, c), (r+moveDirection, c-1), self.board, isPawnPromotion=pawnPromotion))
                    elif (r+moveDirection, c-1) == self.enpassantPossible: #checking if its enpassant square
                        attackingPiece, blockingPiece = self.enpassantPin(r, c, kingRow, kingCol, 0, enemyColor)
                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r+moveDirection, c-1), self.board, isEnpassantMove=True))
        if c+1 <= 7: #captures to the right
            if not piecePinned or pinDirection == (moveDirection, 1):
                if (self.board[r + moveDirection][c + 1][:-2] != 'xx' and not block) or (self.board[r + moveDirection][c + 1][-2:] == 'xx' and block):
                    if self.board[r+moveDirection][c+1][0] == enemyColor: #enemy piece to capture
                        if r+moveDirection == backRow:
                            pawnPromotion = True
                        moves.append(Move((r, c), (r+moveDirection, c+1), self.board, isPawnPromotion=pawnPromotion))
                    elif (r+moveDirection, c+1) == self.enpassantPossible:
                        attackingPiece, blockingPiece = self.enpassantPin(r, c, kingRow, kingCol, 1, enemyColor)
                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r+moveDirection, c+1), self.board, isEnpassantMove=True))

    '''
    Checking if after enpassanting your king is not exposed; in other words, if your enpassant isnt a pin
    '''
    def enpassantPin(self, r, c, kingRow, kingCol, direction, enemyColor):
        attackingPiece = blockingPiece = False
        if kingRow == r:
            if kingCol < c:  # king is left of the pawn
                # inside between king and pawn; outside range between pawn border
                insideRange = range(kingCol + 1, c - 1 + direction)
                outsideRange = range(c + 1 + direction, 8)
            else:  # king right of the pawn
                insideRange = range(kingCol - 1, c + direction, -1)
                outsideRange = range(c - 2 + direction, -1, -1)
            for i in insideRange:
                if self.board[r][i] != "--":  # some other piece beside enpassant pawn blocks
                    blockingPiece = True
                    break
            for i in outsideRange:
                square = self.board[r][i]
                if square[0] == enemyColor and (square[1] == 'R' or square[1] == "Q"):  # attacking piece
                    attackingPiece = True
                    break
                elif square != "--":
                    blockingPiece = True
                    break
        return attackingPiece, blockingPiece

    '''
    Get all the rook moves for the rook located at row, col and add those moves to the list
    '''
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:  # checking if this piece is being pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #cant remove the queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])  # removing the pin from pins for efficiency
                break

        block = True if self.board[r][c][-2:] == 'xx' else False  # 'xx' pieces are unable to move out of xx

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, left, down, right
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8): #can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #check if is on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if (endPiece == "--" and not block) or (endPiece == "--xx" and block): #empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece valid
                            if (endPiece[-2:] != 'xx' and not block) or (endPiece[-2:] == 'xx' and block):
                                moves.append(Move((r, c), (endRow, endCol), self.board))
                                break
                        else: #friendly piece invalid
                            break
                else: #off board
                    break


    '''
    Get all the knight moves for the knight located at row, col and add those moves to the list
    '''

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:  # checking if this piece is being pinned
                piecePinned = True
                self.pins.remove(self.pins[i])  # removing the pin from pins for efficiency
                break

        block = True if self.board[r][c][-2:] == 'xx' else False  # 'xx' pieces are unable to move out of xx

        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) #all knight moves
        allyColor = "w" if self.WhiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #check if is on board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #not an ally piece (empty or enemy piece)
                        if (endPiece[-2:] != 'xx' and not block) or (endPiece[-2:] == 'xx' and block):
                            moves.append(Move((r, c), (endRow, endCol), self.board))
    '''
    Get all the bishop moves for the bishop located at row, col and add those moves to the list
    '''

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:  # checking if this piece is being pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])  # removing the pin from pins for efficiency
                break

        block = True if self.board[r][c][-2:] == 'xx' else False  # 'xx' pieces are unable to move out of xx

        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # up-left, down-left, down-right, up-right
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8): #can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  #check if is on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if (endPiece == "--" and not block) or (endPiece == "--xx" and block):  # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            if (endPiece[-2:] != 'xx' and not block) or (endPiece[-2:] == 'xx' and block):
                                moves.append(Move((r, c), (endRow, endCol), self.board))
                                break
                        else:  # friendly piece invalid
                            break
                else:  # off board
                    break

    '''
    Get all the queen moves for the queen located at row, col and add those moves to the list
    '''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
    Get all the king moves for the king located at row, col and add those moves to the list
    '''

    def getKingMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))  # all king moves
        allyColor = "w" if self.WhiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # check if is on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally piece (empty or enemy piece)
                    #place king on end square and check for checks
                    self.checkAfterKingMove(r, c, endRow, endCol, allyColor, moves)
        self.getCastleMoves(r, c, moves, allyColor)

    '''
    a helping function to check if your king is in check after moving
    '''
    def checkAfterKingMove(self, r, c, endRow, endCol, allyColor, moves, castle=False):
        if allyColor == 'w':
            self.whiteKingLocation = (endRow, endCol)
        else:
            self.blackKingLocation = (endRow, endCol)
        inCheck, pins, checks = self.checkForPinsAndChecks()
        if not inCheck:
            moves.append(Move((r, c), (endRow, endCol), self.board, isCastleMove=castle))
        # place king back on original location
        if allyColor == 'w':
            self.whiteKingLocation = (r, c)
        else:
            self.blackKingLocation = (r, c)

    '''
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    '''
    def getCastleMoves(self, r, c, moves, allyColor):
        if self.checkForPinsAndChecks()[0]:
            return #cant castle while we are in check
        if (self.WhiteToMove and self.currentCastlingRights.wks) or (not self.WhiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)
        if (self.WhiteToMove and self.currentCastlingRights.wqs) or (not self.WhiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)

    def getKingsideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            self.checkAfterKingMove(r, c, r, c+2, allyColor, moves, castle=True)

    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            self.checkAfterKingMove(r, c, r, c-2, allyColor, moves, castle=True)

    '''
    Returns if the player is in check, a list of pins, and a list of checks
    '''
    def checkForPinsAndChecks(self):
        pins = [] #squares where the allied pinned piece is and direction pinned from
        checks = [] #squares where enemy is applying a check
        inCheck = False
        if self.WhiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, 1), (1, -1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[:-2] == 'xx':
                        break
                    if endPiece[0] == allyColor and endPiece[1] != 'K': #prevent your king from protecting himself
                        if possiblePin == (): #1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, so no pin or check possible in this dirrection
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possibilities here in this complex conditional
                        #1.) orthogonally away from king and piece is a rook
                        #2.) diagonally away from king and piece is a bishop
                        #3.) 1 square away diagonally from king and piece is a pawn
                        #4.) any direction away from king and piece is a queen
                        #5.) any direction 1 square away from king and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): #no piece blocking so its check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #piece blocking so its pin
                                pins.append(possiblePin)
                                break
                        else: #enemy piece not applying check
                            break
                else: #is outside the board
                    break
        #check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': #enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    """
    -------------------------------------------Abilities section-------------------------------------------------------
    """

    '''
    Okonogi - Pawn
    '''
    def Okonogi(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:  # checking if this piece is being pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])  # removing the pin from pins for efficiency
                break

        if self.WhiteToMove:
            moveDirection = -1
            backRow = 0
        else:
            moveDirection = 1
            backRow = 7
        pawnPromotion = False  # flag variable

        block = True if self.board[r][c][-2:] == 'xx' else False  # 'xx' pieces are unable to move out of xx

        if c-1 >= 0: #move to the left
            if not piecePinned or pinDirection == (-1, -1):
                if (self.board[r+moveDirection][c-1] == "--" and not block) or (self.board[r + moveDirection][c - 1] == "--xx" and block): #not ally piece
                    if r+moveDirection == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r+moveDirection, c-1), self.board, isPawnPromotion=pawnPromotion))

        if c+1 <= 7: #move to the right
            if not piecePinned or pinDirection == (moveDirection, 1):
                if (self.board[r+moveDirection][c+1] == "--" and not block) or (self.board[r+moveDirection][c+1] == "--xx" and block): #not ally piece
                    if r+moveDirection == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r+moveDirection, c+1), self.board, isPawnPromotion=pawnPromotion))

    '''
    Kanon - Rook
    '''
    def Kanon(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:  # checking if this piece is being pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # cant remove the queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])  # removing the pin from pins for efficiency
                break

        allyColor = 'w' if self.WhiteToMove else 'b'
        enemyColor = "b" if self.WhiteToMove else "w"

        block = True if self.board[r][c][-2:] == 'xx' else False  # 'xx' pieces are unable to move out of xx

        if self.KanonRookPermission: #appending moves from the last turn
            nop = self.currentKanonRookNr #number of package
            if not piecePinned:
                for move in range(self.currentKanonRook[nop].length): #unpacking the coordinates package
                    cords = self.currentKanonRook[nop].cords[move]
                    if self.board[cords[0]][cords[1]][0] == enemyColor:
                        if (self.board[cords[0]][cords[1]][-2:] != 'xx' and not block) or (self.board[cords[0]][cords[1]][-2:] == 'xx' and block):
                            moves.append(Move((r, c), cords, self.board))
                #print(self.currentKanonRook)
                self.currentKanonRook.remove(self.currentKanonRook[nop])
        #print(self.currentKanonRookNr)
        firstKanonRook = []
        self.currentKanonRookNr = None
        self.KanonRookPermission = False
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        for d in directions:
            for i in range(1, 8):  # can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # check if is on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space valid
                            continue
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            firstKanonRook.append((endRow, endCol)) #packing all our coordinates into one package
                            break
                        else:  # friendly piece invalid
                            break
                else:  # off board
                    break
        if len(firstKanonRook) > 0:
            self.currentKanonRook.append(KanonShanonRookSpecialMove(firstKanonRook, allyColor)) #storing all packages

    '''
    Shanon - Rook
    '''
    def Shanon(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:  # checking if this piece is being pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # can't remove the queen from pin on rook moves
                    self.pins.remove(self.pins[i])  # removing the pin from pins for efficiency
                break

        allyColor = 'w' if self.WhiteToMove else 'b'
        enemyColor = "b" if self.WhiteToMove else "w"

        block = True if self.board[r][c][-2:] == 'xx' else False  # 'xx' pieces are unable to move out of xx

        if self.ShanonRookPermission:  # appending moves from the last turn
            nop = self.currentShanonRookNr  # number of package
            if not piecePinned:
                for move in range(self.currentShanonRook[nop].length):  # unpacking the coordinates package
                    cords = self.currentShanonRook[nop].cords[move]
                    if self.board[cords[0]][cords[1]][0] == enemyColor:
                        if (self.board[cords[0]][cords[1]][-2:] != 'xx' and not block) or (self.board[cords[0]][cords[1]][-2:] == 'xx' and block):
                            moves.append(Move((r, c), cords, self.board))
                #print(self.currentShanonRook)
                self.currentShanonRook.remove(self.currentShanonRook[nop])
        #print(self.currentShanonRookNr)
        firstShanonRook = []
        self.currentShanonRookNr = None
        self.ShanonRookPermission = False
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        for d in directions:
            for i in range(1, 8):  # can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # check if is on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space valid
                            continue
                        elif endPiece[0] == allyColor:  # enemy piece valid
                            firstShanonRook.append((endRow, endCol))  # packing all our coordinates into one package
                            break
                        else:  # friendly piece invalid
                            break
                else:  # off board
                    break
        if len(firstShanonRook) > 0:
            self.currentShanonRook.append(KanonShanonRookSpecialMove(firstShanonRook, allyColor)) #storing all packages

    '''
    Akasaka - Queen
    '''
    def Akasaka(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:  # checking if this piece is being pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])  # removing the pin from pins for efficiency
                break

        enemyColor = "b" if self.WhiteToMove else "w"
        block = True if self.board[r][c][-2:] == 'xx' else False  # 'xx' pieces are unable to move out of xx

        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # up-left, down-left, down-right, up-right
        for d in directions:
            for i in range(1, 16):  # can move max 15 squares
                x = i if c + i < 8 else i - 8 #come from other side if came to a wall
                endRow = r + d[0] * i
                endCol = c + d[1] * x
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # check if is on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if (endPiece == "--" and not block) or (endPiece == "--xx" and block):  # empty space valid
                            if c + i >= 8: #only appending moves from his special ability
                                moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            if (endPiece[-2:] != 'xx' and not block) or (endPiece[-2:] != 'xx' and block):
                                if c + i >= 8:
                                    moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:  # off board
                    break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        for d in directions:
            for i in range(1, 16):  # can move max 15 squares
                x = i if c + i < 8 else i - 8
                endRow = r + d[0] * i
                endCol = c + d[1] * x
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # check if is on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if (endPiece == "--" and not block) or (endPiece == "--xx" and block):  # empty space valid
                            if c + i >= 8: #only appending moves from his special ability
                                moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            if (endPiece[-2:] != 'xx' and not block) or (endPiece[-2:] != 'xx' and block):
                                if c + i >= 8:
                                    moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:  # off board
                    break

    '''
    Kraus - pawn - does nothing other than his Order so we will skip this function
    here we will keep all pieces that we can pass
    '''
    def Kraus(self, r, c, moves):
        pass

    def ShanonFurniture(self, r, c, moves):
        pass

    '''
    moduł rykoszetu
    x = i if c + i < 8 or c - i > 0 else abs(i - 8)  # come from other side if came to a wall
    '''

    """
    -----------------------------------------------ORDERS--------------------------------------------------------------
    """

    '''
    Kraus - pawn
    '''
    def krausOrder(self, r, c, orders):
        if self.WhiteToMove:
            moveDirection = -1
            enemyColor = 'b'
            allyColor = 'w'
        else:
            moveDirection = 1
            enemyColor = 'w'
            allyColor = 'b'

        #getValidOrders
        if not self.orderPlaced and self.ordersAccess['Kraus' + allyColor]:
            if self.board[r+moveDirection][c][0] == enemyColor: #1 square pawn advance
                if self.board[r + 2 * moveDirection][c] == "--" and self.board[r + moveDirection][c][1] != 'K':  # cant push king
                    #can push only if square behind is empty
                    orders.append(Order((r, c), (r+moveDirection, c), self.board, 'Kraus'))
        #Order itself
        elif self.ordersAccess['Kraus' + allyColor]:
            self.board[r+2*moveDirection][c] = self.board[r+moveDirection][c] #enemy appears in new location
            self.board[r+moveDirection][c] = "--" #deleting enemy from old location
            self.ordersAccess['Kraus' + allyColor] = False
            self.orderPlaced = False
        #undoing Order
        elif self.undoOrder:
            self.board[r + moveDirection][c] = self.board[r+2*moveDirection][c] #get enemy back to its previous location
            self.board[r + 2 * moveDirection][c] = "--" #remove him from the place he was before
            self.ordersAccess['Kraus' + allyColor] = True #restore order access
            self.undoOrder = False

    '''
    Shannon - furniture - knight
    '''
    def shanonFurnitureOrder(self, r, c, orders):
        if self.WhiteToMove:
            allyColor = 'w'
        else:
            allyColor = 'b'
        squares = [(0, 0), (1, 0), (0, 1), (1, 1)]

        # getValidOrders
        if not self.orderPlaced and self.ordersAccess['Shanon-furniture' + allyColor]:
            for row in range(len(self.board) - 1):
                for col in range(len(self.board[row]) - 1):
                    orders.append(Order((r, c), (row, col), self.board, 'Shanon-furniture'))
        # Order itself
        elif self.ordersAccess['Shanon-furniture' + allyColor]:
            for sq in squares:
                self.board[orders.endRow + sq[0]][orders.endCol + sq[1]] += "xx"
                self.shanonFurnitureBarrierCords.append((orders.endRow + sq[0], orders.endCol + sq[1]))
                print(self.board[orders.endRow + sq[0]][orders.endCol + sq[1]])
            self.shanonFurnitureBarrierStatus = 4
            #self.shanonFurnitureBarrierCords.append(allyColor)
            self.ordersAccess['Shanon-furniture' + allyColor] = False
            self.orderPlaced = False
        # undoing Order
        elif self.undoOrder:
            self.shanonFurnitureBarrierStatus += 1
            self.undoOrder = False
            if self.shanonFurnitureBarrierStatus == 5:
                # allyColor = self.shanonFurnitureBarrierCords.pop()
                self.shanonFurnitureBarrierStatus = 0
                for x in range(4):
                    cords = self.shanonFurnitureBarrierCords.pop()
                    self.board[cords[0]][cords[1]] = self.board[cords[0]][cords[1]][:-2]
                self.ordersAccess['Shanon-furniturew'] = True  # restore order access
                self.ordersAccess['Shanon-furnitureb'] = True  # restore order access


'''
class responsible for move information
'''
class Move():
    #maps keys to values
    #key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isPawnPromotion=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #pawn promotion
        self.isPawnPromotion = isPawnPromotion
        #PRO TIP: instead of making 'if' statement and changing it to True if its True we can just make this statement the truth itself

        #en passant
        self.isEnpassantMove = isEnpassantMove

        #castle move
        self.isCastleMove = isCastleMove


        self.isCapture = (self.pieceCaptured != '--') or self.isEnpassantMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        moveString = self.pieceMoved[1]
        if moveString == 'P':
            if self.endRow == 0 or self.endRow == 7:
                return self.getRankFile(self.endRow, self.endCol) + "=" + promotedPiece #if promoted we add =Q for example
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + self.getRankFile(self.endRow, self.endCol) #if piece captures
            else:
                return self.getRankFile(self.endRow, self.endCol) #if its pawn we dont need P in front
        if self.isCastleMove: #if its castle
            return "O-O" if self.endCol == 6 else "O-O-O"
        #normaly show name of piece + end coordinates
        if self.isCapture:
            moveString += 'x'
        return moveString + self.getRankFile(self.endRow, self.endCol)
    #can add + for check and # for checkmate

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

'''
class responsible for Orders
'''
class Order():
    def __init__(self, startsQ, endSq, board, name):
        self.startRow = startsQ[0]
        self.startCol = startsQ[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceOrdered = board[self.startRow][self.startCol]
        self.targetPiece = board[self.endRow][self.endCol]
        self.name = name

        self.moveID = str(self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol) + self.name

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Order):
            return self.moveID == other.moveID
        return False

'''
castling class
'''
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

'''
coordinates for the squares Kanon threatened last turn
'''
class KanonShanonRookSpecialMove():
    def __init__(self, cords, allyColor):
        self.cords = cords
        self.length = len(cords)
        self.allyColor = allyColor









