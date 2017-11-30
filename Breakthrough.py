#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Jake Schurch"
__version__ = "0.0.1"

from random import choice, random


def _coordinate(piece, direction: str):
    X, Y = piece.x, piece.y
    direction = direction.lower()

    if direction == 'n':
        return (X + 1, Y + 0)
    elif direction == 'nw':
        return (X + 1, Y + -1)
    elif direction == 'ne':
        return (X + 1, Y + 1)
    elif direction == 's':
        return (X + -1, Y + 0)
    elif direction == 'se':
        return (X + -1, Y + 1)
    elif direction == 'sw':
        return (X + -1, Y + -1)


class Board(object):
    """docstring for Board"""

    def __init__(self, N=5):
        self.state = []
        self.rows = N
        self.cols = N

        for c in range(1, self.cols + 1):
            self.state.append(Piece(2, 1, c))
            self.state.append(Piece(1, self.rows, c))

    def __repr__(self):
        i = 1
        output = ""

        for piece in self.get_physical_state():
            output += str(piece) + " "
            i += 1

            if i % self.rows - 1 == 0:
                output += "\n"
                i = 1

        return output

    def check_if_result(self):  # type: str or None
        if any(piece for piece in self.state
               if piece.team == 1 and piece.x == 1):
            return 'win'

        if any(piece for piece in self.state
               if piece.team == 2 and piece.x == self.rows):
            return 'lose'

        return None  # no result; continue Game

    def get_physical_state(self):  # type: list[Piece or None]
        physical_state = []
        for r in range(self.rows, 0, -1):
            for c in range(1, self.cols + 1):
                index, piece_at_pos = self.find(r, c)

                if piece_at_pos is not None:
                    physical_state.append(piece_at_pos)
                else:
                    physical_state.append(".")
        # print(r, c)   # DEBUG STATE
        return physical_state

    def move_piece(self, piece, newX: int, newY: int):  # type: list
        self.state[piece].x = newX
        self.state[piece].y = newY

        return self.state

    def find(self, x: int, y: int):  # type: Piece or None
        for index, piece in enumerate(self.state):
            if x == piece.x and y == piece.y:
                return index, piece
        else:
            return None, None


class Piece(object):
    """docstring for Piece"""
    __slots__ = ['team', 'x', 'y']  # ignore / for efficiency purposes

    _pieces = ['.', 'X', 'O']

    def __init__(self, team: int, x: int, y: int):
        self.team = team
        self.x = x
        self.y = y

    def __repr__(cls):
        return cls._pieces[cls.team]

    def SetNewPos(self, newPos: tuple):  # type: None
        self.x = newPos[0]
        self.y = newPos[1]

    def get_valid_moves(self, state):
        valid_moves = []
        err = None

        if self.team == 1:
            direction = 's'
        else:
            direction = 'n'

        # XXX: What about weast?
        west_move = _coordinate(self, direction + 'w')
        if (repr(state.find(west_move[0], west_move[1])[1]) is not repr(self)
                and not (self.y < 1)):
            valid_moves.append(west_move)

        east_move = _coordinate(self, direction + 'e')

        if (repr(state.find(east_move[0], east_move[1])[1]) != repr(self)
                and not (self.y > state.cols)):
            valid_moves.append(east_move)

        vertical_move = _coordinate(self, direction)
        if repr(state.find(vertical_move[0], vertical_move[1])) != repr(self):
            valid_moves.append(vertical_move)

        if len(valid_moves) is 0:
            err = 1
        return valid_moves, err


class MemoryMove(object):
    """docstring for RememberedMove"""
    def __init__(self, board):
        self.state = board
        self.ranked_moves = dict

    def __repr__(self):
        return self.state.get_physical_state()

    def GetTopRankedMove(self):
        top_ranked_moves = list
        top_ranked = max(self.ranked_moves.values())
        top_ranked_moves = [k for k, v in iter(self.ranked_moves)
                            if v == top_ranked]

        return random.choice(top_ranked_moves)

    def GetRandomMove(self):
        return random.choice([k for k, v in iter(self.ranked_moves)])


class Agent(object):
    """docstring for Agent"""

    def __init__(self):
        self.team = int
        self.wins = 0
        self.loses = 0
        self.ties = 0

    def get_moves(self, board):  # type: list
        pieces = []
        for piece in board.state:
            if piece.team == self.team:
                valid_moves, err = piece.get_valid_moves(board)

                if err != 1:
                    pieces.append({(piece.x, piece.y): valid_moves})
                else:
                    pass
        # print(pieces)  # DEBUG STATEMENT
        return pieces

    def make_move(self, board):
        """ Allows agent to select a position to move a piece. """
        return


class Random_Agent(Agent):
    """docstring for Random_Agent"""

    def __init__(self):
        super().__init__()

    def get_moves(self, board):
        return super().get_moves(board)

    def make_move(self, board):  # type: Board
        moves = self.get_moves(board)
        pieceToMove = moves[choice(range(0, len(moves)))]

        originalPos = next(iter(pieceToMove.keys()))
        newPos = self._select_random_move(pieceToMove.values())
        pieceIndex, piece = board.find(originalPos[0], originalPos[1])

        try:
            ItoDel, toDel = board.find(newPos[0], newPos[1])
            del toDel
        except TypeError:
            pass

        board.state[pieceIndex].SetNewPos(newPos)

        return board

    def _select_random_move(self, moveset):
        output = choice([v for v in list(moveset)[0]])
        return output


class Smart_Agent(Agent):
    """docstring for Smart_Agent"""
    def __init__(self, alpha=0.3, gamma=0.9, epsilon=0.1):
        super().__init__()
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # memory rate
        self.epsilon = epsilon  # prob. of random move
        self.memory_moves = set
        self.last_action_taken = None
        self.last_state_seen = None
        self.move_count = 0

    def get_moves(self, board):
        return super().get_moves(board)

    def make_move(self, board):
        # state not yet seen, score moves as 0.0
        if board.get_physical_state() not in self.memory_moves:
            mem_move = MemoryMove(board)
            for action in self.get_moves(board):
                mem_move.ranked_moves[action] = 0.0
            self.memory_moves.add(mem_move)

        if random.random() <= epsilon:
            action = self.memory_moves[physical_state].GetRandomMove()
        else:
            action = self.memory_moves[physical_state].GetTopRankedMove()

        # QUESTION: is last action taken regarding other player?
        # TODO: implement scoring function
        return action

    def score_move(self):
        return NotImplementedError


class Game(object):
    """docstring for Game"""
    __slots__ = [
        'player1', 'player2', 'games', 'game_moves', 'board', 'board_size',
        'yourTurn'
    ]

    def __init__(self, player1, player2, board_size=5):
        # self.games = dict
        # self.game_moves = list
        self.board_size = board_size

        self.player1 = player1
        self.player2 = player2
        self.board = Board(board_size)

        self.player1.team = 1
        self.player2.team = 2
        self.yourTurn = self.player1

    def Play(self, NumberOfGames=1):
        for n in range(NumberOfGames):

            while self.board.check_if_result() is None:
                self.board = self.yourTurn.make_move(self.board)

                if self.yourTurn.team == 1:
                    self.yourTurn = self.player2
                else:
                    self.yourTurn = self.player1

            self._recordResult(self.board)
            self._resetBoard(self.board)

        print("player 1 number of Wins: {0}, Loses: {1}".format(
            self.player1.wins, self.player1.loses))

    def _recordResult(self, board):
        if self.board.check_if_result() == 'win':
            self.player1.wins += 1
            self.player2.loses += 1
        else:
            self.player1.loses += 1
            self.player2.wins += 1

    def _resetBoard(self, board):
        self.board = Board(self.board_size)


if __name__ == '__main__':
    g = Game(Random_Agent(), Random_Agent())
    g.Play(1000)
