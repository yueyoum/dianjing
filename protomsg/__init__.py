
MESSAGE_TO_ID = {
    "UTCNotify": 10,
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
    "ClubSetPolicyRequest": 410,
    "ClubSetPolicyResponse": 411,
    "ClubSetMatchStaffRequest": 412,
    "ClubSetMatchStaffResponse": 413,
    "StaffNotify": 500,
    "StaffRemoveNotify": 501,
    "StaffTrainingRequest": 502,
    "StaffTrainingResponse": 503,
    "StaffTrainingGetRewardRequest": 504,
    "StaffTrainingGetRewardResponse": 505,
    "StaffRecruitNotify": 520,
    "StaffRecruitRefreshRequest": 521,
    "StaffRecruitRefreshResponse": 522,
    "StaffRecruitRequest": 523,
    "StaffRecruitResponse": 524,
    "StaffFireRequest": 525,
    "StaffFireResponse": 526,
    "LeagueNotify": 600,
    "LeagueGetStatisticsRequest": 601,
    "LeagueGetStatisticsResponse": 602,
    "LeagueGetBattleLogRequest": 603,
    "LeagueGetBattleLogResponse": 604,
    "ChallengeNotify": 700,
    "ChallengeStartRequest": 701,
    "ChallengeStartResponse": 702,
    "BuildingNotify": 800,
    "BuildingLevelUpRequest": 801,
    "BuildingLevelUpResponse": 802,
    "TrainingNotify": 900,
    "TrainingRemoveNotify": 901,
    "TrainingBuyRequest": 902,
    "TrainingBuyResponse": 903,
    "SkillNotify": 1000,
    "SkillLockToggleRequest": 1001,
    "SkillLockToggleResponse": 1002,
    "SkillWashRequest": 1003,
    "SkillWashResponse": 1004,
    "TaskNotify": 1100,
    "TaskAcquireRequest": 1101,
    "TaskAcquireResponse": 1102,
    "TaskGetRewardRequest": 1103,
    "TaskGetRewardResponse": 1104,
    "FriendNotify": 1200,
    "FriendRemoveNotify": 1201,
    "FriendGetInfoRequest": 1202,
    "FriendGetInfoResponse": 1203,
    "FriendAddRequest": 1204,
    "FriendAddResponse": 1205,
    "FriendRemoveRequest": 1206,
    "FriendRemoveResponse": 1207,
    "FriendMatchRequest": 1208,
    "FriendMatchResponse": 1209,
    "FriendAcceptRequest": 1210,
    "FriendAcceptResponse": 1211,
}

ID_TO_MESSAGE = {
    10: "UTCNotify",
    100: "GetServerListRequest",
    101: "GetServerListResponse",
    102: "StartGameRequest",
    103: "StartGameResponse",
    200: "RegisterRequest",
    201: "RegisterResponse",
    202: "LoginRequest",
    203: "LoginResponse",
    300: "CharacterNotify",
    301: "CreateCharacterRequest",
    302: "CreateCharacterResponse",
    400: "ClubNotify",
    401: "CreateClubRequest",
    402: "CreateClubResponse",
    410: "ClubSetPolicyRequest",
    411: "ClubSetPolicyResponse",
    412: "ClubSetMatchStaffRequest",
    413: "ClubSetMatchStaffResponse",
    500: "StaffNotify",
    501: "StaffRemoveNotify",
    502: "StaffTrainingRequest",
    503: "StaffTrainingResponse",
    504: "StaffTrainingGetRewardRequest",
    505: "StaffTrainingGetRewardResponse",
    520: "StaffRecruitNotify",
    521: "StaffRecruitRefreshRequest",
    522: "StaffRecruitRefreshResponse",
    523: "StaffRecruitRequest",
    524: "StaffRecruitResponse",
    525: "StaffFireRequest",
    526: "StaffFireResponse",
    600: "LeagueNotify",
    601: "LeagueGetStatisticsRequest",
    602: "LeagueGetStatisticsResponse",
    603: "LeagueGetBattleLogRequest",
    604: "LeagueGetBattleLogResponse",
    700: "ChallengeNotify",
    701: "ChallengeStartRequest",
    702: "ChallengeStartResponse",
    800: "BuildingNotify",
    801: "BuildingLevelUpRequest",
    802: "BuildingLevelUpResponse",
    900: "TrainingNotify",
    901: "TrainingRemoveNotify",
    902: "TrainingBuyRequest",
    903: "TrainingBuyResponse",
    1000: "SkillNotify",
    1001: "SkillLockToggleRequest",
    1002: "SkillLockToggleResponse",
    1003: "SkillWashRequest",
    1004: "SkillWashResponse",
    1100: "TaskNotify",
    1101: "TaskAcquireRequest",
    1102: "TaskAcquireResponse",
    1103: "TaskGetRewardRequest",
    1104: "TaskGetRewardResponse",
    1200: "FriendNotify",
    1201: "FriendRemoveNotify",
    1202: "FriendGetInfoRequest",
    1203: "FriendGetInfoResponse",
    1204: "FriendAddRequest",
    1205: "FriendAddResponse",
    1206: "FriendRemoveRequest",
    1207: "FriendRemoveResponse",
    1208: "FriendMatchRequest",
    1209: "FriendMatchResponse",
    1210: "FriendAcceptRequest",
    1211: "FriendAcceptResponse",
}

PATH_TO_REQUEST = {
    "/game/servers/": ["server", "GetServerListRequest"],
    "/game/start/": ["server", "StartGameRequest"],
    "/game/account/register/": ["account", "RegisterRequest"],
    "/game/account/login/": ["account", "LoginRequest"],
    "/game/character/create/": ["character", "CreateCharacterRequest"],
    "/game/club/create/": ["club", "CreateClubRequest"],
    "/game/club/policy/": ["club", "ClubSetPolicyRequest"],
    "/game/club/matchstaff/": ["club", "ClubSetMatchStaffRequest"],
    "/game/staff/training/": ["staff", "StaffTrainingRequest"],
    "/game/staff/training/getreward/": ["staff", "StaffTrainingGetRewardRequest"],
    "/game/staff/recruit/refresh/": ["staff", "StaffRecruitRefreshRequest"],
    "/game/staff/recruit/": ["staff", "StaffRecruitRequest"],
    "/game/staff/fire/": ["staff", "StaffFireRequest"],
    "/game/league/statistics/": ["league", "LeagueGetStatisticsRequest"],
    "/game/league/log/": ["league", "LeagueGetBattleLogRequest"],
    "/game/challenge/start/": ["challenge", "ChallengeStartRequest"],
    "/game/building/levelup/": ["building", "BuildingLevelUpRequest"],
    "/game/training/buy/": ["training", "TrainingBuyRequest"],
    "/game/skill/locktoggle/": ["skill", "SkillLockToggleRequest"],
    "/game/skill/wash/": ["skill", "SkillWashRequest"],
    "/game/task/acquire/": ["task", "TaskAcquireRequest"],
    "/game/task/getreward/": ["task", "TaskGetRewardRequest"],
    "/game/friend/info/": ["friend", "FriendGetInfoRequest"],
    "/game/friend/add/": ["friend", "FriendAddRequest"],
    "/game/friend/remove/": ["friend", "FriendRemoveRequest"],
    "/game/friend/match/": ["friend", "FriendMatchRequest"],
    "/game/friend/accept/": ["friend", "FriendAcceptRequest"],
}

PATH_TO_RESPONSE = {
    "/game/servers/": ["server", "GetServerListResponse"],
    "/game/start/": ["server", "StartGameResponse"],
    "/game/account/register/": ["account", "RegisterResponse"],
    "/game/account/login/": ["account", "LoginResponse"],
    "/game/character/create/": ["character", "CreateCharacterResponse"],
    "/game/club/create/": ["club", "CreateClubResponse"],
    "/game/club/policy/": ["club", "ClubSetPolicyResponse"],
    "/game/club/matchstaff/": ["club", "ClubSetMatchStaffResponse"],
    "/game/staff/training/": ["staff", "StaffTrainingResponse"],
    "/game/staff/training/getreward/": ["staff", "StaffTrainingGetRewardResponse"],
    "/game/staff/recruit/refresh/": ["staff", "StaffRecruitRefreshResponse"],
    "/game/staff/recruit/": ["staff", "StaffRecruitResponse"],
    "/game/staff/fire/": ["staff", "StaffFireResponse"],
    "/game/league/statistics/": ["league", "LeagueGetStatisticsResponse"],
    "/game/league/log/": ["league", "LeagueGetBattleLogResponse"],
    "/game/challenge/start/": ["challenge", "ChallengeStartResponse"],
    "/game/building/levelup/": ["building", "BuildingLevelUpResponse"],
    "/game/training/buy/": ["training", "TrainingBuyResponse"],
    "/game/skill/locktoggle/": ["skill", "SkillLockToggleResponse"],
    "/game/skill/wash/": ["skill", "SkillWashResponse"],
    "/game/task/acquire/": ["task", "TaskAcquireResponse"],
    "/game/task/getreward/": ["task", "TaskGetRewardResponse"],
    "/game/friend/info/": ["friend", "FriendGetInfoResponse"],
    "/game/friend/add/": ["friend", "FriendAddResponse"],
    "/game/friend/remove/": ["friend", "FriendRemoveResponse"],
    "/game/friend/match/": ["friend", "FriendMatchResponse"],
    "/game/friend/accept/": ["friend", "FriendAcceptResponse"],
}
