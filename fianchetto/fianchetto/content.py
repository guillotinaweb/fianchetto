from guillotina import configure, content, schema
from guillotina.directives import index_field
from guillotina.interfaces import IFolder


class IChessGame(IFolder):

    index_field("users", type="keyword")
    white = schema.TextLine(title="White player", required=False)
    black = schema.TextLine(title="Black player", required=False)
    moves = schema.List(value_type=schema.TextLine(), default=list())


@configure.contenttype(type_name="ChessGame", schema=IChessGame)
class ChessGame(content.Folder):
    """ ChessGame class """

    def validate_move(self, move):
        return True
