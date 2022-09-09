from hashlib import new
from re import L
from player import Player
from random import randint
import numpy as np
from board import Board
from copy import deepcopy
from collections import Counter
import utils 


class AIPlayer(Player):
    """This player should implement a heuristic along with a min-max and alpha
    beta search to """
	
    def __init__(self):

        self.name = "Alpha Do"
    
    def getColumn(self, board):

        return self.alphabeta(board)

    
    def alphabeta(self, board: Board, maxdepth=4):
        
        def getWinner(board, pos):

            """
            Returns the player (boolean) who won, or None if nobody won
            """

            tests = []
            tests.append(board.getCol(pos[0]))
            tests.append(board.getRow(pos[1]))
            tests.append(board.getDiagonal(True, pos[0] - pos[1]))
            tests.append(board.getDiagonal(False, pos[0] + pos[1]))

            for test in tests:
                color, size = utils.longest(test)
                if size >= 4 :
                    if color == 1 :
                        return 1
                    elif color == -1 :
                        return -1
                    return None


        def getHeuristic(board, last_pos) :
            
            """ 
            Compute the number of alignments possible for a given position and the number of token with the same color in each alignement 
            """

            winner = getWinner(board, last_pos)
            
            #si win : +42069
            if winner == self.color:
                return 1000000
            #si loose : -42069
            if winner == -self.color:
                return -1000000

            #si la board est full, égalié, on retourne 0
            if board.isFull():
                return 0

            IA_score = get_score(board, self.color)

            return IA_score


        def score_diag_down(board, shift_diag_down, color) :

            """ Compute score on a given down diag """

            diag_down_line = board.getDiagonal(up=False, shift=shift_diag_down)
            if isImportant(diag_down_line) and (len(diag_down_line) >= 4) :
                diag_down_score = getLineAlignmentsPossible(diag_down_line, color)
                return diag_down_score
            else :
                return 0


        def score_diag_up(board, shift_diag_up, color) :

            """ Compute score on a given down diag """

            diag_up_line = board.getDiagonal(up=True, shift=shift_diag_up)
            if isImportant(diag_up_line) and (len(diag_up_line) >= 4) :
                diag_up_score = getLineAlignmentsPossible(diag_up_line, color)
                return diag_up_score
            else :
                return 0


        def get_score(board, color) :

            """ Compute the score of the entire board """

            score = 0

            for row in range(6) :
                
                col = row

                # We compute the score for each direction and sum it
                horizontal_line = board.getRow(row)
                if isImportant(horizontal_line) :
                    horizontal_score = getLineAlignmentsPossible(horizontal_line, color=color)
                    score += horizontal_score

                vertical_line = board.getCol(col)
                if isImportant(vertical_line) :
                    vertical_score = getLineAlignmentsPossible(vertical_line, color=color)
                    score += vertical_score

                score += score_diag_down(board, shift_diag_down=row, color=color)
                score += score_diag_down(board, shift_diag_down=row + 6, color=color)

            # Diag up score
            score += score_diag_up(board, shift_diag_up=0, color=color)
            for shift in range(1, 7) :
                score += score_diag_up(board, shift_diag_up=shift, color=color)
                score += score_diag_up(board, shift_diag_up=-shift, color=color)

            # Last column
            vertical_line = board.getCol(6)
            if isImportant(vertical_line) :
                vertical_score = getLineAlignmentsPossible(vertical_line, color)
                score += vertical_score

            return score


        def isEmpty(line) :

            """ Indicates if a given line is empty """
            
            n_boxes = len(line)

            return Counter(line)[0] == n_boxes


        def isFull(line) :

            """ Indicates if a given line is full """

            return not(0 in line)


        def isImportant(line) :

            """ Indicates if a line is important, i.e. not empty nor full """

            return not(isFull(line) or isEmpty(line))


        def getLineAlignmentsPossible(line, color) :
        
            """ 
            Compute the number of alignments possible for a given line

            line -> list : the current line
            """

            # Number of boxes in the line
            n_boxes = len(line)

            # We initialize the sliding window : it is on the left of the row
            start_box = 0
            end_box = 3

            # Variable which counts the number of alignments and their "strength"
            alignments = 0

            # We stop when the sliding window reach the end of the columns
            while end_box < n_boxes :
                
                window = line[start_box:end_box+1]

                # If there is a blue token, it means the alignment is not possible in the sliding window
                if -color in window :
                    pass
                # Else it means an alignment is possible and its strength corresponds to the number of friendly tokens in the window
                else :
                    alignments += Counter(window)[color]

                # We move the sliding window to the right
                start_box += 1
                end_box += 1

            return alignments


        def isLeaf(board: Board,depth,last_pos):

            """
            isLeaf évalue si un point est une feuille
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
            if isLeaf(board,depth,last_pos): 
                # On renvoie l'euristique de la feuille
                return getHeuristic(board,last_pos)
            
            new_alpha = -np.inf
            # Sinon on balaie pour toutes less colonne jouabless
            for column in board.getPossibleColumns():
                # On créée la nouvelle board
                child = deepcopy(board)
                last_pos=(column, child.play(self.color,column)) #c'est à l'adversaire de jouer, donc -self.color (on choisi le max des mins choisis par l'adversaire)

                # On calcule alpha qui est le max des mins que l'ennemi choisit, ie choisir la MinValue la plus grande
                new_alpha = max(new_alpha,minValue(child,alpha,beta,depth+1,last_pos))

                #Condition de dépassement (alpha est croissante et beta est décroissante, mais alpha < beta. en effet on cherche le alpha le plus grand parmi les beta. si unn beta )
                #On fait grandir alpha jusqu'à ce qu'il dépasse beta. Bof claire mais ok
                if new_alpha >= beta:
                    return new_alpha #Ssi alpha >= beta on coupe! on saute la branche
                alpha = max(alpha, new_alpha)
            return new_alpha
        

        
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

            if isLeaf(board,depth,last_pos): # Si on est sur une feuille
                return getHeuristic(board,last_pos)  # On renvoie l'euristique de la feuille
            
            new_beta = np.inf
            for column in board.getPossibleColumns():
                child = deepcopy(board)
                last_pos = (column, child.play(-self.color,column)) #c'est à nous de jouer, donc self.color (l'adversaire choisi le min des max choisispar nous)
                new_beta = min(new_beta,maxValue(child,alpha,beta,depth+1,last_pos))
                if alpha >= new_beta: # Condition d'elagage
                    return new_beta # On coupe la branche
                beta = min(beta,new_beta)
            return new_beta
        

        #Retourner la colone à jouer. Donc on balaie les colones
        alpha_max = -np.inf
        beta_min = np.inf
        columns = board.getPossibleColumns()
        final_choice = 0
        last_pos = (0,0)
        for col in columns:
            newboard = deepcopy(board)
            last_pos = (col,newboard.play(self.color,col))
            new_alpha = minValue(newboard,alpha_max,beta_min,1,last_pos)
            if alpha_max < new_alpha:
                alpha_max = new_alpha
                final_choice = col
        return final_choice