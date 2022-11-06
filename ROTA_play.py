import requests
import json
import numpy as np
from ROTA_DP import ROTA_DP, buildStates

class ROTA_player:
    def __init__ (self, states):
        self.base_url = 'https://rota.praetorian.com/rota/service/play.php'
        self.cookies = None
        self.board = np.zeros([9])
        self.player = 1
        self.oppPlayer = 2
        self.states = states
        self.policies = [np.empty((self.states.shape[0]), dtype='object'), np.empty((self.states.shape[0]), dtype='object')]
        self.games_won = 0
        self.moves = 0
        self.done=False
    
    def startGame(self):
        print('\nStarting Session...')
        res = requests.get(self.base_url, params = {'request':'new', 'email':'me@me.me'})
        self.cookies = res.cookies
        boardString = res.json()['data']['board']
        print(f'Started New Game\n{res.json()["data"]}')
        self.setPlayer(boardString)
        self.setBoard(boardString)
    
    def createPolicy(self):
        dp_1 = ROTA_DP(self.states, 1)
        dp_2 = ROTA_DP(self.states, 2)
        print('Creating policy for Player 1...')
        self.policies[0] = dp_1.trainAndGetPolicy()
        print('\nCreating policy for Player 2...')
        self.policies[1] = dp_2.trainAndGetPolicy()

    def setBoard(self, boardString):
        charMap = {'-':0, 'c' : self.oppPlayer, 'p':self.player}
        for i, char in enumerate(boardString):
            self.board[i] = charMap[char]

    def updateStatus(self):
        requests.get(self.base_url,params={'request':'status'}, cookies=self.cookies )

    def place(self, x):
        res = requests.get(self.base_url, params={'request': 'place', 'location': x+1}, cookies=self.cookies).json()
        print(res["data"])
        self.setBoard(res['data']['board'])
    
    def move(self, x, y):
        res = requests.get(self.base_url, params={'request':'move', 'from': x+1, 'to': y+1}, cookies=self.cookies).json()
        print(res["data"])
        self.setBoard(res['data']['board'])
        self.moves=res['data']['moves']

    def makeMove(self):
        moveInd = np.where(np.all(self.states == self.board, axis=1))
        move = self.policies[self.player-1][moveInd[0][0]]
        if move[1] is not None:
            self.move(move[0], move[1])
        else:
            self.place(move[0])

    def next(self):
        res = requests.get(self.base_url, params={'request':'next'}, cookies=self.cookies).json()
        if 'hash' in res['data'].keys():
            print('Done!')
            print(f'Hash: {res["data"]["hash"]}')
            self.done = True
        else:
            print(f'Started Next Game\n{res["data"]}')
            self.games_won +=1
            boardString = res['data']['board']
            self.moves = res['data']['moves']
            self.setPlayer(boardString)
            self.setBoard(boardString)

    
    def setPlayer(self,boardString):
        self.player = 2 if boardString.count('c') else 1
        self.oppPlayer = 1 if self.player==2 else 2

def main(): 
    player = ROTA_player(buildStates())
    player.createPolicy()
    player.startGame()
    while not player.done:
        while player.moves < 30:
            player.makeMove()
        player.next()

if __name__ == '__main__':
    main()

