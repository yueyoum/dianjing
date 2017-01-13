
-module(dj_protocol_mapping).
-export([get_name/1,
    get_id/1]).

-include("dj_protocol.hrl").


get_name(50) ->
    'ProtoSocketConnectRequest';

get_name(4802) ->
    'ProtoPartyRoomRequest';

get_name(4804) ->
    'ProtoPartyCreateRequest';

get_name(4806) ->
    'ProtoPartyJoinRequest';

get_name(4808) ->
    'ProtoPartyQuitRequest';

get_name(4810) ->
    'ProtoPartyKickRequest';

get_name(4812) ->
    'ProtoPartyChatRequest';

get_name(4814) ->
    'ProtoPartyBuyRequest';

get_name(4816) ->
    'ProtoPartyStartRequest';

get_name(4818) ->
    'ProtoPartyDismissRequest';

get_name(_) ->
    undefined.


get_id(#'ProtoSocketConnectResponse'{}) ->
    51;

get_id(#'ProtoPartyInfoNotify'{}) ->
    4800;

get_id(#'ProtoPartyMessageNotify'{}) ->
    4801;

get_id(#'ProtoPartyRoomResponse'{}) ->
    4803;

get_id(#'ProtoPartyCreateResponse'{}) ->
    4805;

get_id(#'ProtoPartyJoinResponse'{}) ->
    4807;

get_id(#'ProtoPartyQuitResponse'{}) ->
    4809;

get_id(#'ProtoPartyKickResponse'{}) ->
    4811;

get_id(#'ProtoPartyChatResponse'{}) ->
    4813;

get_id(#'ProtoPartyBuyResponse'{}) ->
    4815;

get_id(#'ProtoPartyStartResponse'{}) ->
    4817;

get_id(#'ProtoPartyDismissResponse'{}) ->
    4819.
