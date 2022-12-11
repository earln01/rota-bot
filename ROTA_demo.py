import numpy as np
import sys
from ROTA_DP import buildStates

class ROTA_Interactive:
    def __init__(self, player1File, player2File):
        self.board = np.zeros([9])
        self.player = 0
        self.oppPlayer = 0
        self.policies = [np.load(player1File, allow_pickle=True), np.load(player2File, allow_pickle=True)]
        self.winners = np.array([[0,1,2], [3,4,5],[6,7,8],[0,4,8],[2,4,6],[0,3,6],[1,4,7],[2,5,8],[5,7,8],[3,6,7],[0,1,3],[1,2,5]])
        self.states = buildStates()
    

    def playGame(self):
        self.startGame()
        self.printBoard()
        while True:
            if self.player == 1:
                self.makeComputerMove()
                self.printBoard()
                done = self.checkWin(self.board, self.player)
                if done:
                    print('I Beat You!')
                    break
                self.makePlayerMove()
                self.printBoard()
                done = self.checkWin(self.board, self.oppPlayer)
                if done:
                    print('You Beat Me!')
                    break
            else:
                self.makePlayerMove()
                self.printBoard()
                done = self.checkWin(self.board, self.oppPlayer)
                if done:
                    print('You Beat Me!')
                    break
                self.makeComputerMove()
                self.printBoard()
                done = self.checkWin(self.board, self.player)
                if done:
                    print('I Beat You!')
                    break
    def reset(self):
        self.board = np.zeros([9])
    
    def setPlayer(self, player):
        self.player = 1 if player != 1 else 2
        self.oppPlayer = player

    def startGame(self):
        player = 0
        while player not in ['1', '2']:
            player = input("Would you like to play player 1 or player 2?: ")
            if player not in ['1','2']:
                print('Please enter 1 or 2.')
        self.setPlayer(int(player))
    
    def printBoard(self):
        printer  = np.reshape(self.board, (-1, 3)).astype(int)
        np.savetxt(sys.stdout, printer, fmt = '%d')
    
    def makeComputerMove(self):
        moveInd = np.where(np.all(self.states == self.board, axis=1))
        move = self.policies[self.player-1][moveInd[0][0]]
        if move[1] is not None:
            self.move(move[0], move[1])
            print(f'I moved from square {move[0]+1} to square {move[1]+1}')
        else:
            self.place(move[0], self.player)
            print(f'I placed my piece at square {move[0]+1}')
    
    def makePlayerMove(self):
        pos, moveDesc, place = self.getLegalMoves(self.board, self.oppPlayer)
        if place:
            given = ''
            moves = [move[0]+1 for move in moveDesc]
            while given not in [str(move) for move in moves]:
                given = input(f'Choose a location to place your piece from the options {moves}: ')
                if given not in [str(move) for move in moves]:
                    print('Not a legal option. Try again.')
            self.place(int(given)-1, self.oppPlayer)
        else:
            check = [(str(move[0]+1), str(move[1]+1)) for move in moveDesc]
            src = ''
            dst = ''
            while (src, dst) not in check:
                print(f'Choose a move from the options {[(move[0]+1, move[1]+1) for move in moveDesc]}, format (from, to).')
                src = input('From: ')
                dst = input('To: ')
                if (src, dst) not in check:
                    print('Not a legal option. Try Again.')
            self.move(int(src)-1, int(dst)-1)

    
    def place(self, x, player):
        self.board[x] = player
    
    def move(self, x, y):
        player = self.board[x]
        self.board[x] = 0
        self.board[y] = player
    
    def getLegalMoves(self, board, player):
        pieces = len(board[board==player])
        moves = []
        moveDesc = []
        place = False
        if player == 1 and len(board[board==2]) != pieces:
            return [np.array(moves), moveDesc, place]
        if pieces < 3:
            place=True
            if player == 2 and not len(board[board==1]) > pieces:
                return [np.array(moves), moveDesc, place]
            else:
                for ind in np.argwhere(board == 0):
                    legalMove = np.copy(board)
                    legalMove[ind] = player
                    moves.append(legalMove)
                    moveDesc.append((ind[0], None))
        else:
            for ind in np.argwhere(board==player):
                possibleMoves = self.getAdjacent(ind[0])
                for move in possibleMoves:
                    if board[move] == 0:
                        legalMove = np.copy(board)
                        legalMove[move] = player
                        legalMove[ind[0]] = 0
                        moves.append(legalMove)
                        moveDesc.append((ind[0],move))
        return [np.array(moves), moveDesc, place]

    def getAdjacent(self, index):
        if index==4:
            return set([i for i in range(9) if i != 4])
        row, col = divmod(index, 3)
        adjacent =set([4])
        for i in [row-1, row+1]:
            if i>=0 and i<=2:
                adjacent.add(i*3 +col)
        for j in [col-1, col+1]:
            if j>=0 and j<=2:
                adjacent.add(row*3 +j)
        return adjacent

    def checkWin(self, board, player):
        if not len(board[board==player])>=3:
            return False
        else:
            playerInds = np.sort(np.argwhere(board==player)).flatten()
            if np.any(np.equal(self.winners, playerInds).all(1)):
                return True
        return False



if __name__ == '__main__':
    demo = ROTA_Interactive('player1.npy', 'player2.npy')
    while True:
        demo.playGame()
        again = ''
        while again.upper() not in ['Y', 'N']:
            again = input('\nPlay Again? (Y/N): ')
        if again.upper() == 'N':
            break
        demo.reset()