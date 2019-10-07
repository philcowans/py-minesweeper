# Copyright (c) 2019 Philip J Cowans
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from flask import Flask, jsonify, request
from random import randrange

app = Flask('py-minesweeper')

class Game:
    def __init__(self):
        self.board = [[self._generate_square() for i in range(20)] for j in range(20)]
        self.hidden_squares = 20 * 20
        for i in range(10):
            self.board[randrange(20)][randrange(20)]['has_mine'] = True
        for i in range(20):
            for j in range(20):
                self.board[i][j]['neighbourhood_count'] = self._count_neighbours(i, j)

    def reveal(self, i, j):
        if (i < 0) or (i >= 19) or (j < 0) or (j >= 19):
            return
        if self.board[i][j]['visible']:
            return
        self.board[i][j]['visible'] = True
        self.hidden_squares -= 1
        if self.board[i][j]['has_mine'] or (self.board[i][j]['neighbourhood_count'] > 0):
            return
        self.reveal(i + 1, j)
        self.reveal(i - 1, j)
        self.reveal(i, j + 1)
        self.reveal(i, j - 1)

    def _count_neighbours(self, i, j):
        n = 0
        for delta_i in range(-1, 2):
            for delta_j in range(-1, 2):
                if (delta_i + i >= 0) and (delta_i + i < 20) and (delta_j + j >= 0) and (delta_j + j < 20):
                    if self.board[delta_i + i][delta_j + j]['has_mine']:
                        n += 1
        return n

    def _generate_square(self):
        return {
            'has_mine': False,
            'neighbourhood_count': None,
            'visible': False
        }

game = Game()

@app.route('/board', methods=['GET'])
def board():
    results = []
    for i in range(20):
        for j in range(20):
            results += [{
                'row': i,
                'column': j,
                'neighbourhood_count': game.board[i][j]['neighbourhood_count'],
                'visible': game.board[i][j]['visible']
            }]
    return jsonify(results)

@app.route('/moves', methods=['POST'])
def moves():
    content = request.json
    game.reveal(content['row'], content['column'])
    if game.board[content['row']][content['column']]['has_mine']:
        return {'status': 'fail'}
    elif game.hidden_squares == 10:
        return {'status': 'success'}
    else:
        return {'status': 'in_progress'}
