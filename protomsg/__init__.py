
MESSAGE_TO_ID = {
    "GetServerListRequest": 100,
    "GetServerListResponse": 101,
    "StartGameRequest": 102,
    "StartGameResponse": 103,
    "RegisterRequest": 200,
    "RegisterResponse": 201,
    "LoginRequest": 202,
    "LoginResponse": 203,
    "CharacterNotify": 300,
    "CreateCharacterRequest": 301,
    "CreateCharacterResponse": 302,
    "ClubNotify": 400,
    "CreateClubRequest": 401,
    "CreateClubResponse": 402,
}
PATH_TO_MESSAGE = {
    "/servers/": ["server", "GetServerListRequest"],
    "/start/": ["server", "StartGameRequest"],
    "/account/register/": ["account", "RegisterRequest"],
    "/account/login/": ["account", "LoginRequest"],
    "/character/create/": ["character", "CreateCharacterRequest"],
    "/club/create/": ["club", "CreateClubRequest"],
}