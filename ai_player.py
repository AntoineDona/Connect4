from hashlib import new
from re import L
from player import Player
from random import randint
import numpy as np
from board import Board
from copy import deepcopy
from collections import Counter
import utils 

# *********** LOGGER ***********
import config
logger = config.LOGGER 

class AIPlayer(Player):
    """This player should implement a heuristic along with a min-max and alpha
    beta search to """
	
    def __init__(self):
        self.name = "Alpha Do"
    
    def getColumn(self, board):
         # TODO(student): implement this!
        logger.info(board)

        availableColumns = board.getPossibleColumns()
        logger.info(availableColumns)
        column_id = randint(0,len(availableColumns))

        #En fonction de l'état de la grille, pour chaque coup que l'ia peut jouer, calculer 
        #On étend l'arbre jusqu'à une profondeur h 
        #On calcule à cette profondeur la fonction euristique pour les neuds terminaux ou alors jusqu'à une victoire
        #Back propager avec alpha beta


        #return availableColumns[column_id]
        return self.alphabeta(board)

    
    def alphabeta(self,board: Board,maxdepth = 4):
        
              
        def getWinner(board, pos):
            """
            Returns the player (boolean) who won, or None if nobody won
            """
            tests = []
            tests.append(board.getCol(pos[0]))
            tests.append(board.getRow(pos[1]))
            tests.append(board.getDiagonal(True, pos[0] - pos[1]))
            tests.append(board.getDiagonal(False, pos[0] + pos[1]))
            logger.info(tests)

            for test in tests:
                color, size = utils.longest(test)
                if size >= 4:
                    if color == 1:
                        return 1
                    elif color == -1:
                        return -1
                    return None


        def getEuristic(board,last_pos) :
            """ 
            Compute the number of alignments possible for a given position and the number of token with the same color in each alignement 
            """
            score = 0
            
            #si win : +42069
            if getWinner(board,last_pos) == self.color:
                score += 42069
            #si loose : -42069
            if getWinner(board,last_pos) == -self.color:
                score -= 42069

            #si la board est full, égalié, on retourne 0
            if board.isFull():
                return 0

            scores = np.zeros((6,7))

            for col in range(7):
                row = 0
                while (row < 6 and board[col][row] != 0 ):
                    pos = (row,col)
                    # We check how many alignments are possible for each direction
                    vertical_direction_alignment = getVerticalAlignmentPossible(board, pos)
                    horizontal_direction_alignment = getHorizontalAlignmentPossible(board, pos)
                    scores[row][col] = (vertical_direction_alignment + horizontal_direction_alignment)*board[col][row]

                    row +=1
            
            return np.sum(scores)


        def getVerticalAlignmentPossible(board, pos) :

            """ 
            Compute the number of alignments possible for a given position and direction 

            board -> Board : the state of the current game
            pos -> couple : position of the current token
            """

            # Unpack position
            row, col = pos

            # logger.info("ROW = {}".format(row))

            # Get the state in the current column
            line = board.getCol(col)

            # Variable which will store the amount of friendly tokens already put 
            friendly_tokens = 0
            # Variable designating the numero of the box currently observed 
            box_num = row

            # We go through the tokens already put
            while (box_num >= 0) and (line[box_num] == 1) :
                # While we see a friendly token, we count it. We stop when we see a hostile token
                friendly_tokens += 1
                # Move on to the box below
                box_num -= 1

            # Variable that holds the number of free boxes to allow an alignment
            necessary_boxes = 4 - friendly_tokens
            # Variable that holds the number of free boxes left
            free_boxes = Counter(line)[0]

            # If there is not enough space, 0 alignment can be achieved
            if free_boxes < necessary_boxes :
                return 0
            # Else, we return the number of friendly token of the possibe alignment
            else :
                return friendly_tokens


        def getHorizontalAlignmentPossible(board, pos) :
        
            """ 
            Compute the number of alignments possible for a given position and direction 

            board -> Board : the state of the current game
            pos -> couple : position of the current token
            """

            # Unpack position
            row, col = pos

            # logger.info("COL = {}".format(col))

            # Get the state in the current column
            line = board.getRow(row)

            # We initialize the sliding window : it is on the left of the row
            start_box = 0
            end_box = 3

            # Variable which counts the number of alignments and their "strength"
            alignments = 0

            # We stop when the sliding window reach the end of the columns
            while end_box < 7 :

                # logger.info("start_box = {}".format(start_box))
                # logger.info("end_box = {}".format(end_box))
                
                window = line[start_box:end_box+1]
                # logger.info("window = {}".format(window))


                # If there is a blue token, it means the alignment is not possible in the sliding window
                if -1 in window :
                    # logger.info("alignment = {}".format(0))
                    pass
                # Else it means an alignment is possible and its strength corresponds to the number of friendly tokens in the window
                else :
                    alignments += Counter(window)[1]
                    # logger.info("alignment = {}".format(Counter(window)[1]))

                # We move the sliding window to the right
                start_box += 1
                end_box += 1

            # logger.info("alignments = {}".format(alignments))
            # logger.info("")

            return alignments


        def isLeaf(board: Board,depth,last_pos):
            #en fonction de la profondeur ou fin de partie?
            """
            isNode évalue si un point est une feuille
            retourne un booleen
            """
            return depth >= maxdepth or getWinner(board,last_pos) != None or board.isFull()
        

        def maxValue(board: Board,alpha,beta, depth,last_pos):

            """
            maxValue évalue le niveau AMI (calcul d'alpha)

            retourne alpha, le meilleur alpha, cad le plus grand
            -------------------------------------------------------------
            paramètres:
            - board: plateau de jeu courant
            - alpha: meilleure  evaluation courante AMI
            - beta: meilleure evaluation courante ENNEMIE
            - dpeth: profondeur de l'arbre

            """
        
            # Si on est sur une feuille
            # logger.info("maxval isLeaf")
            if isLeaf(board,depth,last_pos): 
                # On renvoie l'euristique de la feuille

                return getEuristic(board,last_pos)
            
            # Sinon on balaie pour toutes less colonne jouabless
            for column in board.getPossibleColumns():
                #on créée la nouvelle board
                child = deepcopy(board)
                # print("child = ", child)
                # print("type of child = ", type(child))
                last_pos=(column, child.play(-self.color,column)) #c'est à l'adversaire de jouer, donc -self.color (on choisi le max des mins choisis par l'adversaire)
                # logger.info(child)

                # logger.info("type of child= {}".format(type(child)))
                # logger.info("child= {}".format(child))

                # On calcule alpha qui est le max des mins que l'ennemi choisit, ie choisir la MinValue la plus grande
                # print("Calling minValues")
                alpha = max(alpha,minValue(child,alpha,beta,depth+1,last_pos))

                #Condition de dépassement (alpha est croissante et beta est décroissante, mais alpha < beta. en effet on cherche le alpha le plus grand parmi les beta. si unn beta )
                #On fait grandir alpha jusqu'à ce qu'il dépasse beta. Bof claire mais ok
                if alpha >= beta:
                    return beta #Ssi alpha >= beta on coupe! on saute la branche
            return alpha
        

        
        def minValue(board: Board,alpha,beta,depth,last_pos):

            """
            minValue évalue le niveau ENNEMI (calcul de beta)

            retourne beta, le meilleur beta, cad le plus petit
            -------------------------------------------------------------
            paramètres:
            - board: plateau de jeu courants
            - alpha: meilleure  evaluation courante AMI
            - beta: meilleure evaluation courante ENNEMIE

            """
            # logger.info("type of board = {}".format(type(board)))
            # logger.info("minval isLeaf")
            if isLeaf(board,depth,last_pos): # Si on est sur une feuille
                return getEuristic(board,last_pos)  # On renvoie l'euristique de la feuille
            
            for column in board.getPossibleColumns():
                child = deepcopy(board)
                last_pos = (column, child.play(self.color,column)) #c'est à nous de jouer, donc self.color (l'adversaire choisi le min des max choisispar nous)
                # logger.info(child)
                # print("calling maxValue")
                logger.info(getWinner(board,last_pos))
                beta = min(beta,maxValue(child,alpha,beta,depth+1,last_pos))
                if alpha >= beta: # Condition d'elagage
                    return alpha # On coupe la branche
            return beta
        

        #Retourner la colone à jouer. Donc on balaie les colones
        alpha_max = -np.inf
        beta_min = np.inf
        columns = board.getPossibleColumns()
        depth = 0
        final_choice = 0
        last_pos = (0,0)
        for col in columns:
            newboard = deepcopy(board)
            last_pos = (col,newboard.play(self.color,col))
            new_alpha = maxValue(newboard,alpha_max,beta_min,depth,last_pos)
            logger.info("newalpha = {}".format(new_alpha))
            if alpha_max < new_alpha:
                alpha_max = new_alpha
                final_choice = col
        logger.info(alpha_max)
        return final_choice