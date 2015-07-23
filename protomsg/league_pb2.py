# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: league.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import common_pb2
import match_pb2
import club_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='league.proto',
  package='Dianjing.protocol',
  serialized_pb='\n\x0cleague.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\x1a\x0bmatch.proto\x1a\nclub.proto\"\x80\x05\n\x06League\x12-\n\x05level\x18\x01 \x02(\x0e\x32\x1e.Dianjing.protocol.LeagueLevel\x12\x15\n\rcurrent_order\x18\x02 \x02(\x05\x12\x33\n\x05\x63lubs\x18\x03 \x03(\x0b\x32$.Dianjing.protocol.League.LeagueClub\x12\x33\n\x05ranks\x18\x04 \x03(\x0b\x32$.Dianjing.protocol.League.LeagueRank\x12\x35\n\x06\x65vents\x18\x05 \x03(\x0b\x32%.Dianjing.protocol.League.LeagueEvent\x1a_\n\nLeagueRank\x12\x16\n\x0eleague_club_id\x18\x01 \x02(\t\x12\x14\n\x0c\x62\x61ttle_times\x18\x02 \x02(\x05\x12\r\n\x05score\x18\x03 \x02(\x05\x12\x14\n\x0cwinning_rate\x18\x04 \x02(\x05\x1a\xe0\x01\n\x0bLeagueEvent\x12\x11\n\tbattle_at\x18\x01 \x02(\x05\x12\x10\n\x08\x66inished\x18\x02 \x02(\x08\x12?\n\x05pairs\x18\x03 \x03(\x0b\x32\x30.Dianjing.protocol.League.LeagueEvent.LeaguePair\x1ak\n\nLeaguePair\x12\x0f\n\x07pair_id\x18\x01 \x02(\t\x12\x1a\n\x12league_club_one_id\x18\x02 \x02(\t\x12\x1a\n\x12league_club_two_id\x18\x03 \x02(\t\x12\x14\n\x0c\x63lub_one_win\x18\x04 \x02(\x08\x1aK\n\nLeagueClub\x12\x16\n\x0eleague_club_id\x18\x01 \x02(\t\x12%\n\x04\x63lub\x18\x02 \x02(\x0b\x32\x17.Dianjing.protocol.Club\"J\n\x0cLeagueNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12)\n\x06league\x18\x02 \x02(\x0b\x32\x19.Dianjing.protocol.League\"9\n\x1aLeagueGetStatisticsRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\t\"\x96\x02\n\x1bLeagueGetStatisticsResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12S\n\nstatistics\x18\x03 \x03(\x0b\x32?.Dianjing.protocol.LeagueGetStatisticsResponse.LeagueStatistics\x1a\x83\x01\n\x10LeagueStatistics\x12\x10\n\x08staff_id\x18\x01 \x02(\x05\x12\x1e\n\x16winning_rate_to_terran\x18\x02 \x02(\x05\x12\x1c\n\x14winning_rate_to_zerg\x18\x03 \x02(\x05\x12\x1f\n\x17winning_rate_to_protoss\x18\x04 \x02(\x05\"=\n\x19LeagueGetBattleLogRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0f\n\x07pair_id\x18\x02 \x02(\t\"k\n\x1aLeagueGetBattleLogResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12/\n\tmatch_log\x18\x03 \x01(\x0b\x32\x1c.Dianjing.protocol.ClubMatch')




_LEAGUE_LEAGUERANK = _descriptor.Descriptor(
  name='LeagueRank',
  full_name='Dianjing.protocol.League.LeagueRank',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='league_club_id', full_name='Dianjing.protocol.League.LeagueRank.league_club_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='battle_times', full_name='Dianjing.protocol.League.LeagueRank.battle_times', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='score', full_name='Dianjing.protocol.League.LeagueRank.score', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='winning_rate', full_name='Dianjing.protocol.League.LeagueRank.winning_rate', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=316,
  serialized_end=411,
)

_LEAGUE_LEAGUEEVENT_LEAGUEPAIR = _descriptor.Descriptor(
  name='LeaguePair',
  full_name='Dianjing.protocol.League.LeagueEvent.LeaguePair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pair_id', full_name='Dianjing.protocol.League.LeagueEvent.LeaguePair.pair_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='league_club_one_id', full_name='Dianjing.protocol.League.LeagueEvent.LeaguePair.league_club_one_id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='league_club_two_id', full_name='Dianjing.protocol.League.LeagueEvent.LeaguePair.league_club_two_id', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='club_one_win', full_name='Dianjing.protocol.League.LeagueEvent.LeaguePair.club_one_win', index=3,
      number=4, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=531,
  serialized_end=638,
)

_LEAGUE_LEAGUEEVENT = _descriptor.Descriptor(
  name='LeagueEvent',
  full_name='Dianjing.protocol.League.LeagueEvent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='battle_at', full_name='Dianjing.protocol.League.LeagueEvent.battle_at', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='finished', full_name='Dianjing.protocol.League.LeagueEvent.finished', index=1,
      number=2, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pairs', full_name='Dianjing.protocol.League.LeagueEvent.pairs', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_LEAGUE_LEAGUEEVENT_LEAGUEPAIR, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=414,
  serialized_end=638,
)

_LEAGUE_LEAGUECLUB = _descriptor.Descriptor(
  name='LeagueClub',
  full_name='Dianjing.protocol.League.LeagueClub',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='league_club_id', full_name='Dianjing.protocol.League.LeagueClub.league_club_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='club', full_name='Dianjing.protocol.League.LeagueClub.club', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=640,
  serialized_end=715,
)

_LEAGUE = _descriptor.Descriptor(
  name='League',
  full_name='Dianjing.protocol.League',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='level', full_name='Dianjing.protocol.League.level', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='current_order', full_name='Dianjing.protocol.League.current_order', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='clubs', full_name='Dianjing.protocol.League.clubs', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ranks', full_name='Dianjing.protocol.League.ranks', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='events', full_name='Dianjing.protocol.League.events', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_LEAGUE_LEAGUERANK, _LEAGUE_LEAGUEEVENT, _LEAGUE_LEAGUECLUB, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=75,
  serialized_end=715,
)


_LEAGUENOTIFY = _descriptor.Descriptor(
  name='LeagueNotify',
  full_name='Dianjing.protocol.LeagueNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.LeagueNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='league', full_name='Dianjing.protocol.LeagueNotify.league', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=717,
  serialized_end=791,
)


_LEAGUEGETSTATISTICSREQUEST = _descriptor.Descriptor(
  name='LeagueGetStatisticsRequest',
  full_name='Dianjing.protocol.LeagueGetStatisticsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.LeagueGetStatisticsRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.LeagueGetStatisticsRequest.id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=793,
  serialized_end=850,
)


_LEAGUEGETSTATISTICSRESPONSE_LEAGUESTATISTICS = _descriptor.Descriptor(
  name='LeagueStatistics',
  full_name='Dianjing.protocol.LeagueGetStatisticsResponse.LeagueStatistics',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.LeagueGetStatisticsResponse.LeagueStatistics.staff_id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='winning_rate_to_terran', full_name='Dianjing.protocol.LeagueGetStatisticsResponse.LeagueStatistics.winning_rate_to_terran', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='winning_rate_to_zerg', full_name='Dianjing.protocol.LeagueGetStatisticsResponse.LeagueStatistics.winning_rate_to_zerg', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='winning_rate_to_protoss', full_name='Dianjing.protocol.LeagueGetStatisticsResponse.LeagueStatistics.winning_rate_to_protoss', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=1000,
  serialized_end=1131,
)

_LEAGUEGETSTATISTICSRESPONSE = _descriptor.Descriptor(
  name='LeagueGetStatisticsResponse',
  full_name='Dianjing.protocol.LeagueGetStatisticsResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.LeagueGetStatisticsResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.LeagueGetStatisticsResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='statistics', full_name='Dianjing.protocol.LeagueGetStatisticsResponse.statistics', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_LEAGUEGETSTATISTICSRESPONSE_LEAGUESTATISTICS, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=853,
  serialized_end=1131,
)


_LEAGUEGETBATTLELOGREQUEST = _descriptor.Descriptor(
  name='LeagueGetBattleLogRequest',
  full_name='Dianjing.protocol.LeagueGetBattleLogRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.LeagueGetBattleLogRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pair_id', full_name='Dianjing.protocol.LeagueGetBattleLogRequest.pair_id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=1133,
  serialized_end=1194,
)


_LEAGUEGETBATTLELOGRESPONSE = _descriptor.Descriptor(
  name='LeagueGetBattleLogResponse',
  full_name='Dianjing.protocol.LeagueGetBattleLogResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.LeagueGetBattleLogResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.LeagueGetBattleLogResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='match_log', full_name='Dianjing.protocol.LeagueGetBattleLogResponse.match_log', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=1196,
  serialized_end=1303,
)

_LEAGUE_LEAGUERANK.containing_type = _LEAGUE;
_LEAGUE_LEAGUEEVENT_LEAGUEPAIR.containing_type = _LEAGUE_LEAGUEEVENT;
_LEAGUE_LEAGUEEVENT.fields_by_name['pairs'].message_type = _LEAGUE_LEAGUEEVENT_LEAGUEPAIR
_LEAGUE_LEAGUEEVENT.containing_type = _LEAGUE;
_LEAGUE_LEAGUECLUB.fields_by_name['club'].message_type = club_pb2._CLUB
_LEAGUE_LEAGUECLUB.containing_type = _LEAGUE;
_LEAGUE.fields_by_name['level'].enum_type = common_pb2._LEAGUELEVEL
_LEAGUE.fields_by_name['clubs'].message_type = _LEAGUE_LEAGUECLUB
_LEAGUE.fields_by_name['ranks'].message_type = _LEAGUE_LEAGUERANK
_LEAGUE.fields_by_name['events'].message_type = _LEAGUE_LEAGUEEVENT
_LEAGUENOTIFY.fields_by_name['league'].message_type = _LEAGUE
_LEAGUEGETSTATISTICSRESPONSE_LEAGUESTATISTICS.containing_type = _LEAGUEGETSTATISTICSRESPONSE;
_LEAGUEGETSTATISTICSRESPONSE.fields_by_name['statistics'].message_type = _LEAGUEGETSTATISTICSRESPONSE_LEAGUESTATISTICS
_LEAGUEGETBATTLELOGRESPONSE.fields_by_name['match_log'].message_type = match_pb2._CLUBMATCH
DESCRIPTOR.message_types_by_name['League'] = _LEAGUE
DESCRIPTOR.message_types_by_name['LeagueNotify'] = _LEAGUENOTIFY
DESCRIPTOR.message_types_by_name['LeagueGetStatisticsRequest'] = _LEAGUEGETSTATISTICSREQUEST
DESCRIPTOR.message_types_by_name['LeagueGetStatisticsResponse'] = _LEAGUEGETSTATISTICSRESPONSE
DESCRIPTOR.message_types_by_name['LeagueGetBattleLogRequest'] = _LEAGUEGETBATTLELOGREQUEST
DESCRIPTOR.message_types_by_name['LeagueGetBattleLogResponse'] = _LEAGUEGETBATTLELOGRESPONSE

class League(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class LeagueRank(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _LEAGUE_LEAGUERANK

    # @@protoc_insertion_point(class_scope:Dianjing.protocol.League.LeagueRank)

  class LeagueEvent(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType

    class LeaguePair(_message.Message):
      __metaclass__ = _reflection.GeneratedProtocolMessageType
      DESCRIPTOR = _LEAGUE_LEAGUEEVENT_LEAGUEPAIR

      # @@protoc_insertion_point(class_scope:Dianjing.protocol.League.LeagueEvent.LeaguePair)
    DESCRIPTOR = _LEAGUE_LEAGUEEVENT

    # @@protoc_insertion_point(class_scope:Dianjing.protocol.League.LeagueEvent)

  class LeagueClub(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _LEAGUE_LEAGUECLUB

    # @@protoc_insertion_point(class_scope:Dianjing.protocol.League.LeagueClub)
  DESCRIPTOR = _LEAGUE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.League)

class LeagueNotify(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LEAGUENOTIFY

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.LeagueNotify)

class LeagueGetStatisticsRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LEAGUEGETSTATISTICSREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.LeagueGetStatisticsRequest)

class LeagueGetStatisticsResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class LeagueStatistics(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _LEAGUEGETSTATISTICSRESPONSE_LEAGUESTATISTICS

    # @@protoc_insertion_point(class_scope:Dianjing.protocol.LeagueGetStatisticsResponse.LeagueStatistics)
  DESCRIPTOR = _LEAGUEGETSTATISTICSRESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.LeagueGetStatisticsResponse)

class LeagueGetBattleLogRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LEAGUEGETBATTLELOGREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.LeagueGetBattleLogRequest)

class LeagueGetBattleLogResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LEAGUEGETBATTLELOGRESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.LeagueGetBattleLogResponse)


# @@protoc_insertion_point(module_scope)
