from guillotina import configure

app_settings = {
    "load_utilities": {
        "fianchetto.chess_server_manager": {
            "provides": "fianchetto.interfaces.IChessServerManager",
            "factory": "fianchetto.utility.ChessServerManager",
            "settings": {},
        }
    }
}


def includeme(root):
    """
    custom application initialization here
    """
    configure.scan("fianchetto.permissions")
    configure.scan("fianchetto.interfaces")
    configure.scan("fianchetto.api")
    configure.scan("fianchetto.utility")
    configure.scan("fianchetto.install")
    configure.scan("fianchetto.content")
