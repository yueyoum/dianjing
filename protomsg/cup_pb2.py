# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cup.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import club_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='cup.proto',
  package='Dianjing.protocol',
  serialized_pb='\n\tcup.proto\x12\x11\x44ianjing.protocol\x1a\nclub.proto\"\xd1\x02\n\x03\x43up\x12\r\n\x05order\x18\x01 \x02(\x05\x12.\n\rlast_champion\x18\x02 \x01(\x0b\x32\x17.Dianjing.protocol.Club\x12.\n\x07process\x18\x03 \x02(\x0e\x32\x1d.Dianjing.protocol.CupProcess\x12\x0e\n\x06joined\x18\x04 \x02(\x08\x12&\n\x05\x63lubs\x18\x05 \x03(\x0b\x32\x17.Dianjing.protocol.Club\x12/\n\x06levels\x18\x06 \x03(\x0b\x32\x1f.Dianjing.protocol.Cup.CupLevel\x12\x10\n\x08top_four\x18\x07 \x03(\t\x1a`\n\x08\x43upLevel\x12.\n\x07process\x18\x01 \x02(\x0e\x32\x1d.Dianjing.protocol.CupProcess\x12\x12\n\nmatch_time\x18\x02 \x02(\x03\x12\x10\n\x08\x63lub_ids\x18\x03 \x03(\t\"\'\n\x14\x43upInfomationRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\"Z\n\x15\x43upInfomationResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12#\n\x03\x63up\x18\x03 \x02(\x0b\x32\x16.Dianjing.protocol.Cup\"!\n\x0e\x43upJoinRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\"T\n\x0f\x43upJoinResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12#\n\x03\x63up\x18\x03 \x01(\x0b\x32\x16.Dianjing.protocol.Cup*\xb2\x01\n\nCupProcess\x12\x16\n\x11\x43UP_PROCESS_APPLY\x10\xe8\x07\x12\x18\n\x13\x43UP_PROCESS_PREPARE\x10\xe9\x07\x12\x12\n\x0e\x43UP_PROCESS_32\x10 \x12\x12\n\x0e\x43UP_PROCESS_16\x10\x10\x12\x11\n\rCUP_PROCESS_8\x10\x08\x12\x11\n\rCUP_PROCESS_4\x10\x04\x12\x11\n\rCUP_PROCESS_2\x10\x02\x12\x11\n\rCUP_PROCESS_1\x10\x01')

_CUPPROCESS = _descriptor.EnumDescriptor(
  name='CupProcess',
  full_name='Dianjing.protocol.CupProcess',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CUP_PROCESS_APPLY', index=0, number=1000,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CUP_PROCESS_PREPARE', index=1, number=1001,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CUP_PROCESS_32', index=2, number=32,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CUP_PROCESS_16', index=3, number=16,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CUP_PROCESS_8', index=4, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CUP_PROCESS_4', index=5, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CUP_PROCESS_2', index=6, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CUP_PROCESS_1', index=7, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=639,
  serialized_end=817,
)

CupProcess = enum_type_wrapper.EnumTypeWrapper(_CUPPROCESS)
CUP_PROCESS_APPLY = 1000
CUP_PROCESS_PREPARE = 1001
CUP_PROCESS_32 = 32
CUP_PROCESS_16 = 16
CUP_PROCESS_8 = 8
CUP_PROCESS_4 = 4
CUP_PROCESS_2 = 2
CUP_PROCESS_1 = 1



_CUP_CUPLEVEL = _descriptor.Descriptor(
  name='CupLevel',
  full_name='Dianjing.protocol.Cup.CupLevel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='process', full_name='Dianjing.protocol.Cup.CupLevel.process', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1000,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='match_time', full_name='Dianjing.protocol.Cup.CupLevel.match_time', index=1,
      number=2, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='club_ids', full_name='Dianjing.protocol.Cup.CupLevel.club_ids', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=286,
  serialized_end=382,
)

_CUP = _descriptor.Descriptor(
  name='Cup',
  full_name='Dianjing.protocol.Cup',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='order', full_name='Dianjing.protocol.Cup.order', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='last_champion', full_name='Dianjing.protocol.Cup.last_champion', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='process', full_name='Dianjing.protocol.Cup.process', index=2,
      number=3, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1000,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='joined', full_name='Dianjing.protocol.Cup.joined', index=3,
      number=4, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='clubs', full_name='Dianjing.protocol.Cup.clubs', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='levels', full_name='Dianjing.protocol.Cup.levels', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='top_four', full_name='Dianjing.protocol.Cup.top_four', index=6,
      number=7, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_CUP_CUPLEVEL, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=45,
  serialized_end=382,
)


_CUPINFOMATIONREQUEST = _descriptor.Descriptor(
  name='CupInfomationRequest',
  full_name='Dianjing.protocol.CupInfomationRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CupInfomationRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
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
  serialized_start=384,
  serialized_end=423,
)


_CUPINFOMATIONRESPONSE = _descriptor.Descriptor(
  name='CupInfomationResponse',
  full_name='Dianjing.protocol.CupInfomationResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.CupInfomationResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CupInfomationResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cup', full_name='Dianjing.protocol.CupInfomationResponse.cup', index=2,
      number=3, type=11, cpp_type=10, label=2,
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
  serialized_start=425,
  serialized_end=515,
)


_CUPJOINREQUEST = _descriptor.Descriptor(
  name='CupJoinRequest',
  full_name='Dianjing.protocol.CupJoinRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CupJoinRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
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
  serialized_start=517,
  serialized_end=550,
)


_CUPJOINRESPONSE = _descriptor.Descriptor(
  name='CupJoinResponse',
  full_name='Dianjing.protocol.CupJoinResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.CupJoinResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CupJoinResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cup', full_name='Dianjing.protocol.CupJoinResponse.cup', index=2,
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
  serialized_start=552,
  serialized_end=636,
)

_CUP_CUPLEVEL.fields_by_name['process'].enum_type = _CUPPROCESS
_CUP_CUPLEVEL.containing_type = _CUP;
_CUP.fields_by_name['last_champion'].message_type = club_pb2._CLUB
_CUP.fields_by_name['process'].enum_type = _CUPPROCESS
_CUP.fields_by_name['clubs'].message_type = club_pb2._CLUB
_CUP.fields_by_name['levels'].message_type = _CUP_CUPLEVEL
_CUPINFOMATIONRESPONSE.fields_by_name['cup'].message_type = _CUP
_CUPJOINRESPONSE.fields_by_name['cup'].message_type = _CUP
DESCRIPTOR.message_types_by_name['Cup'] = _CUP
DESCRIPTOR.message_types_by_name['CupInfomationRequest'] = _CUPINFOMATIONREQUEST
DESCRIPTOR.message_types_by_name['CupInfomationResponse'] = _CUPINFOMATIONRESPONSE
DESCRIPTOR.message_types_by_name['CupJoinRequest'] = _CUPJOINREQUEST
DESCRIPTOR.message_types_by_name['CupJoinResponse'] = _CUPJOINRESPONSE

class Cup(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class CupLevel(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _CUP_CUPLEVEL

    # @@protoc_insertion_point(class_scope:Dianjing.protocol.Cup.CupLevel)
  DESCRIPTOR = _CUP

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Cup)

class CupInfomationRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CUPINFOMATIONREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CupInfomationRequest)

class CupInfomationResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CUPINFOMATIONRESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CupInfomationResponse)

class CupJoinRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CUPJOINREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CupJoinRequest)

class CupJoinResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CUPJOINRESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CupJoinResponse)


# @@protoc_insertion_point(module_scope)
