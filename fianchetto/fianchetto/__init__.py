from guillotina import configure

app_settings = {
    # provide custom application settings here...
}


def includeme(root):
    """
    custom application initialization here
    """
    configure.scan("fianchetto.permissions")
    configure.scan("fianchetto.api")
    configure.scan("fianchetto.install")
    configure.scan("fianchetto.content")
