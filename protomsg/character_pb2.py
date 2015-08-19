# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: character.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import common_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='character.proto',
  package='Dianjing.protocol',
  serialized_pb='\n\x0f\x63haracter.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\"s\n\tCharacter\x12\n\n\x02id\x18\x01 \x02(\t\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x0e\n\x06\x61vatar\x18\x03 \x02(\t\x12\x0e\n\x06gender\x18\x04 \x02(\x05\x12\x0b\n\x03\x61ge\x18\x05 \x02(\x05\x12\x12\n\nprofession\x18\x06 \x02(\x05\x12\x0b\n\x03\x64\x65s\x18\x07 \x02(\t\"N\n\x0f\x43haracterNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12*\n\x04\x63har\x18\x02 \x02(\x0b\x32\x1c.Dianjing.protocol.Character\"7\n\x16\x43reateCharacterRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0c\n\x04name\x18\x02 \x02(\t\"m\n\x17\x43reateCharacterResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12\x34\n\x04next\x18\x03 \x01(\x0e\x32\x1e.Dianjing.protocol.NextOperate:\x06OPT_OK')




_CHARACTER = _descriptor.Descriptor(
  name='Character',
  full_name='Dianjing.protocol.Character',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.Character.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='Dianjing.protocol.Character.name', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='avatar', full_name='Dianjing.protocol.Character.avatar', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gender', full_name='Dianjing.protocol.Character.gender', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='age', full_name='Dianjing.protocol.Character.age', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='profession', full_name='Dianjing.protocol.Character.profession', index=5,
      number=6, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='des', full_name='Dianjing.protocol.Character.des', index=6,
      number=7, type=9, cpp_type=9, label=2,
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
  serialized_start=52,
  serialized_end=167,
)


_CHARACTERNOTIFY = _descriptor.Descriptor(
  name='CharacterNotify',
  full_name='Dianjing.protocol.CharacterNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CharacterNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='char', full_name='Dianjing.protocol.CharacterNotify.char', index=1,
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
  serialized_start=169,
  serialized_end=247,
)


_CREATECHARACTERREQUEST = _descriptor.Descriptor(
  name='CreateCharacterRequest',
  full_name='Dianjing.protocol.CreateCharacterRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CreateCharacterRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='Dianjing.protocol.CreateCharacterRequest.name', index=1,
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
  serialized_start=249,
  serialized_end=304,
)


_CREATECHARACTERRESPONSE = _descriptor.Descriptor(
  name='CreateCharacterResponse',
  full_name='Dianjing.protocol.CreateCharacterResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.CreateCharacterResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CreateCharacterResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='next', full_name='Dianjing.protocol.CreateCharacterResponse.next', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=1,
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
  serialized_start=306,
  serialized_end=415,
)

_CHARACTERNOTIFY.fields_by_name['char'].message_type = _CHARACTER
_CREATECHARACTERRESPONSE.fields_by_name['next'].enum_type = common_pb2._NEXTOPERATE
DESCRIPTOR.message_types_by_name['Character'] = _CHARACTER
DESCRIPTOR.message_types_by_name['CharacterNotify'] = _CHARACTERNOTIFY
DESCRIPTOR.message_types_by_name['CreateCharacterRequest'] = _CREATECHARACTERREQUEST
DESCRIPTOR.message_types_by_name['CreateCharacterResponse'] = _CREATECHARACTERRESPONSE

class Character(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CHARACTER

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Character)

class CharacterNotify(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CHARACTERNOTIFY

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CharacterNotify)

class CreateCharacterRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CREATECHARACTERREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CreateCharacterRequest)

class CreateCharacterResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CREATECHARACTERRESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CreateCharacterResponse)


# @@protoc_insertion_point(module_scope)
