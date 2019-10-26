from guillotina import configure

configure.permission("fianchetto.PlayGame", "Can play the game")
configure.permission("fianchetto.ObserveGame", "Can observe the game")

configure.grant(permission="fianchetto.PlayGame", role="guillotina.Owner")
configure.grant(permission="fianchetto.ObserveGame", role="guillotina.Member")
