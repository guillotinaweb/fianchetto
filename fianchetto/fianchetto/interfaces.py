from guillotina.async_util import IAsyncUtility
from guillotina.directives import index_field
from guillotina.interfaces import IFolder
from guillotina import schema


class IChessServerManager(IAsyncUtility):
    pass


class IChessGame(IFolder):

    index_field("white", type="keyword")
    white = schema.TextLine(title="White player", required=False)

    index_field("black", type="keyword")
    black = schema.TextLine(title="Black player", required=False)

    moves = schema.List(value_type=schema.TextLine(), default=list())
