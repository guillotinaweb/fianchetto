import chess
from guillotina import configure, content, schema
from guillotina.component import get_utility
from guillotina.directives import index_field
from guillotina.interfaces import IFolder, IObjectAddedEvent

from .interfaces import IChessServerManager


class IChessGame(IFolder):

    index_field("white", type="keyword")
    white = schema.TextLine(title="White player", required=False)

    index_field("black", type="keyword")
    black = schema.TextLine(title="Black player", required=False)

    moves = schema.List(value_type=schema.TextLine(), default=list())


@configure.contenttype(type_name="ChessGame", schema=IChessGame)
class ChessGame(content.Folder):
    """ ChessGame class """

    @staticmethod
    def validate_moves(moves):
        """ Validates a list of moves
        :param moves: list e.g. ["f2f4", "e7e6", "g2g4", "d8h4"]
        :return: boolean
        """
        board = chess.Board()

        for move in moves:
            move_obj = chess.Move.from_uci(move)
            if move_obj in board.legal_moves:
                board.push(move_obj)
            else:
                return False

    @property
    def turn(self):
        """Compute who's turn is it depending on the number of moves that
        have been done.
        """
        if len(self.moves or []) % 2 == 0:
            return "white"
        return "black"

    def get_side(self, player_id):
        if self.white == player_id:
            return "white"
        elif self.black == player_id:
            return "black"
        raise Exception()


@configure.subscriber(for_=(IChessGame, IObjectAddedEvent))
async def initialize_game(obj, evnt):
    utility = get_utility(IChessServerManager)
    utility.initialize_game(obj)
