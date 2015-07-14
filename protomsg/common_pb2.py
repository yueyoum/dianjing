# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: common.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='common.proto',
  package='Dianjing.protocol',
  serialized_pb='\n\x0c\x63ommon.proto\x12\x11\x44ianjing.protocol\"/\n\tUTCNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x11\n\ttimestamp\x18\x02 \x02(\x03\"*\n\rStaffBaseInfo\x12\n\n\x02id\x18\x01 \x02(\x05\x12\r\n\x05level\x18\x02 \x02(\x05*C\n\x0bNextOperate\x12\n\n\x06OPT_OK\x10\x01\x12\x13\n\x0fOPT_CREATE_CHAR\x10\x02\x12\x13\n\x0fOPT_CREATE_CLUB\x10\x03*3\n\x06\x41\x63tion\x12\x0c\n\x08\x41\x43T_INIT\x10\x01\x12\x0b\n\x07\x41\x43T_ADD\x10\x02\x12\x0e\n\nACT_UPDATE\x10\x03*\xc1\x01\n\x0bLeagueLevel\x12\x12\n\x0eLEAGUE_LEVEL_1\x10\x01\x12\x12\n\x0eLEAGUE_LEVEL_2\x10\x02\x12\x12\n\x0eLEAGUE_LEVEL_3\x10\x03\x12\x12\n\x0eLEAGUE_LEVEL_4\x10\x04\x12\x12\n\x0eLEAGUE_LEVEL_5\x10\x05\x12\x12\n\x0eLEAGUE_LEVEL_6\x10\x06\x12\x12\n\x0eLEAGUE_LEVEL_7\x10\x07\x12\x12\n\x0eLEAGUE_LEVEL_8\x10\x08\x12\x12\n\x0eLEAGUE_LEVEL_9\x10\t*1\n\x08\x43lubType\x12\x12\n\x0e\x43LUB_TYPE_REAL\x10\x01\x12\x11\n\rCLUB_TYPE_NPC\x10\x02')

_NEXTOPERATE = _descriptor.EnumDescriptor(
  name='NextOperate',
  full_name='Dianjing.protocol.NextOperate',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='OPT_OK', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OPT_CREATE_CHAR', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OPT_CREATE_CLUB', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=128,
  serialized_end=195,
)

NextOperate = enum_type_wrapper.EnumTypeWrapper(_NEXTOPERATE)
_ACTION = _descriptor.EnumDescriptor(
  name='Action',
  full_name='Dianjing.protocol.Action',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ACT_INIT', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ACT_ADD', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ACT_UPDATE', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=197,
  serialized_end=248,
)

Action = enum_type_wrapper.EnumTypeWrapper(_ACTION)
_LEAGUELEVEL = _descriptor.EnumDescriptor(
  name='LeagueLevel',
  full_name='Dianjing.protocol.LeagueLevel',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_1', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_2', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_3', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_4', index=3, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_5', index=4, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_6', index=5, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_7', index=6, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_8', index=7, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LEAGUE_LEVEL_9', index=8, number=9,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=251,
  serialized_end=444,
)

LeagueLevel = enum_type_wrapper.EnumTypeWrapper(_LEAGUELEVEL)
_CLUBTYPE = _descriptor.EnumDescriptor(
  name='ClubType',
  full_name='Dianjing.protocol.ClubType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CLUB_TYPE_REAL', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CLUB_TYPE_NPC', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=446,
  serialized_end=495,
)

ClubType = enum_type_wrapper.EnumTypeWrapper(_CLUBTYPE)
OPT_OK = 1
OPT_CREATE_CHAR = 2
OPT_CREATE_CLUB = 3
ACT_INIT = 1
ACT_ADD = 2
ACT_UPDATE = 3
LEAGUE_LEVEL_1 = 1
LEAGUE_LEVEL_2 = 2
LEAGUE_LEVEL_3 = 3
LEAGUE_LEVEL_4 = 4
LEAGUE_LEVEL_5 = 5
LEAGUE_LEVEL_6 = 6
LEAGUE_LEVEL_7 = 7
LEAGUE_LEVEL_8 = 8
LEAGUE_LEVEL_9 = 9
CLUB_TYPE_REAL = 1
CLUB_TYPE_NPC = 2



_UTCNOTIFY = _descriptor.Descriptor(
  name='UTCNotify',
  full_name='Dianjing.protocol.UTCNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.UTCNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='Dianjing.protocol.UTCNotify.timestamp', index=1,
      number=2, type=3, cpp_type=2, label=2,
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
  serialized_start=35,
  serialized_end=82,
)


_STAFFBASEINFO = _descriptor.Descriptor(
  name='StaffBaseInfo',
  full_name='Dianjing.protocol.StaffBaseInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.StaffBaseInfo.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='level', full_name='Dianjing.protocol.StaffBaseInfo.level', index=1,
      number=2, type=5, cpp_type=1, label=2,
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
  serialized_start=84,
  serialized_end=126,
)

DESCRIPTOR.message_types_by_name['UTCNotify'] = _UTCNOTIFY
DESCRIPTOR.message_types_by_name['StaffBaseInfo'] = _STAFFBASEINFO

class UTCNotify(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _UTCNOTIFY

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.UTCNotify)

class StaffBaseInfo(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _STAFFBASEINFO

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffBaseInfo)


# @@protoc_insertion_point(module_scope)
