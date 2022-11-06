import numpy as np
from sympy.utilities.iterables import multiset_permutations

class ROTA_DP:
    def __init__(self, states, player, discount=0.25):
        self.player = player
        self.oppPlayer = 1 if player==2 else 2
        self.nStates = states.shape[0]
        self.states = states
        self.discount = discount
        self.V = np.zeros([self.nStates])
        self.policy = np.empty((self.nStates), dtype='object')
        self.winners = np.array([[0,1,2], [3,4,5],[6,7,8],[0,4,8],[2,4,6],[0,3,6],[1,4,7],[2,5,8],[5,7,8],[3,6,7],[0,1,3],[1,2,5]])
    
    def trainAndGetPolicy(self):
        self.V = self.valueIteration(self.V)
        self.policy = self.extractPolicy(self.V, self.policy)
        return self.policy
        
    def valueIteration(self,initialV, nIterations=np.inf, tolerance=0.01):
        '''Value iteration procedure
        Repeat V(s) <-- max_a R^a + gamma T^a V(s')
        Where s' = argmax(V[argmin(V[legal moves]]))
        Until epsilon < tolerance
        '''

        epsilon = np.inf
        iterId = 0
        V = initialV

        while epsilon>tolerance and iterId < nIterations:
            epsilon = 0
            for state in range(self.nStates):
                oldV = V[state]
                maxEst = -np.inf
                minNext = np.inf
                legalMoves = self.getLegalMoves(board = self.states[state], player=self.player)[0]
                if self.checkWin(self.states[state],self.oppPlayer) or not legalMoves.size:
                    reward = -100
                    minNext = 0
                    maxEst = reward+(self.discount*minNext)
                elif self.checkWin(self.states[state], self.player):
                    reward = 100
                    minNext = 0
                    maxEst = reward+(self.discount*minNext)
                else:
                    for move in range(legalMoves.shape[0]):
                        reward = 1
                        if self.checkWin(legalMoves[move], self.player):
                            minNext = 100
                        else:
                            minNext = self.getMinNext(V, legalMoves[move])
                        update = self.discount*minNext
                        if reward+update > maxEst:
                            maxEst = reward+update
                epsilon = np.max([epsilon, np.abs(oldV - maxEst)])
                V[state] = maxEst
            iterId += 1
            print(f'Iteration: {iterId} Epsilon: {epsilon}')
        return V

    def extractPolicy(self, V, policy):
        for state in range(self.nStates):
            moves, moveDesc = self.getLegalMoves(board = self.states[state], player=self.player)
            bestMove = None
            if not moves.size:
                policy[state] = bestMove
            else:
                maxVal = -np.inf
                for move in range(moves.shape[0]):
                    reward = 1
                    if self.checkWin(moves[move],self.player):
                        minNext = 100
                    else:
                        minNext = self.getMinNext(V, moves[move])
                    update = self.discount*minNext
                    if reward + update > maxVal:
                        maxVal = reward+update
                        bestMove = move
                policy[state] = moveDesc[bestMove]
        return policy

    def getMinNext(self,V, board):
        minNext = np.inf
        oppLegalMoves = self.getLegalMoves(board = board, player=self.oppPlayer)[0]
        for oppMove in range(oppLegalMoves.shape[0]):
            nextMoveInd = np.where(np.all(self.states == oppLegalMoves[oppMove], axis=1))
            nextV = V[nextMoveInd[0][0]]
            if nextV < minNext:
                minNext = nextV
        return minNext
    
    def getLegalMoves(self, board, player):
        pieces = len(board[board==player])
        moves = []
        moveDesc = []
        if player == 1 and len(board[board==2]) != pieces:
            return [np.array(moves), moveDesc]
        if pieces < 3:
            if player == 2 and not len(board[board==1]) > pieces:
                return [np.array(moves), moveDesc]
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
        return [np.array(moves), moveDesc]

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
            

def buildStates():
    board = [0 for i in range(9)]
    boardList = []
    boardList.append(board.copy())
    for i in range(0,6,2):
        board[i] = 1
        boardList.append(board.copy())
        board[i+1] = 2
        boardList.append(board.copy())
    states = []
    for board in boardList:
        for p in multiset_permutations(board):
            states.append(p)
    return np.array(states)
