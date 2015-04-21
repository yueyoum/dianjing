# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: club.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='club.proto',
  package='Dianjing.protocol.club',
  serialized_pb='\n\nclub.proto\x12\x16\x44ianjing.protocol.club\"\x95\x01\n\x04\x43lub\x12\n\n\x02id\x18\x01 \x02(\x05\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x0f\n\x07manager\x18\x03 \x02(\t\x12\x0c\n\x04\x66lag\x18\x04 \x02(\x05\x12\r\n\x05level\x18\x05 \x02(\x05\x12\x0e\n\x06renown\x18\x06 \x02(\x05\x12\x0b\n\x03vip\x18\x07 \x02(\x05\x12\x0b\n\x03\x65xp\x18\x08 \x02(\x05\x12\x0c\n\x04gold\x18\t \x02(\x05\x12\r\n\x05sycee\x18\n \x02(\x05\"I\n\nClubNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12*\n\x04\x63lub\x18\x02 \x02(\x0b\x32\x1c.Dianjing.protocol.club.Club\"@\n\x11\x43reateClubRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x0c\n\x04\x66lag\x18\x03 \x02(\x05\"2\n\x12\x43reateClubResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c')




_CLUB = _descriptor.Descriptor(
  name='Club',
  full_name='Dianjing.protocol.club.Club',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.club.Club.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='Dianjing.protocol.club.Club.name', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='manager', full_name='Dianjing.protocol.club.Club.manager', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='flag', full_name='Dianjing.protocol.club.Club.flag', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='level', full_name='Dianjing.protocol.club.Club.level', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='renown', full_name='Dianjing.protocol.club.Club.renown', index=5,
      number=6, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='vip', full_name='Dianjing.protocol.club.Club.vip', index=6,
      number=7, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='exp', full_name='Dianjing.protocol.club.Club.exp', index=7,
      number=8, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gold', full_name='Dianjing.protocol.club.Club.gold', index=8,
      number=9, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sycee', full_name='Dianjing.protocol.club.Club.sycee', index=9,
      number=10, type=5, cpp_type=1, label=2,
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
  serialized_start=39,
  serialized_end=188,
)


_CLUBNOTIFY = _descriptor.Descriptor(
  name='ClubNotify',
  full_name='Dianjing.protocol.club.ClubNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.club.ClubNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='club', full_name='Dianjing.protocol.club.ClubNotify.club', index=1,
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
  serialized_start=190,
  serialized_end=263,
)


_CREATECLUBREQUEST = _descriptor.Descriptor(
  name='CreateClubRequest',
  full_name='Dianjing.protocol.club.CreateClubRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.club.CreateClubRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='Dianjing.protocol.club.CreateClubRequest.name', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='flag', full_name='Dianjing.protocol.club.CreateClubRequest.flag', index=2,
      number=3, type=5, cpp_type=1, label=2,
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
  serialized_start=265,
  serialized_end=329,
)


_CREATECLUBRESPONSE = _descriptor.Descriptor(
  name='CreateClubResponse',
  full_name='Dianjing.protocol.club.CreateClubResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.club.CreateClubResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.club.CreateClubResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
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
  serialized_start=331,
  serialized_end=381,
)

_CLUBNOTIFY.fields_by_name['club'].message_type = _CLUB
DESCRIPTOR.message_types_by_name['Club'] = _CLUB
DESCRIPTOR.message_types_by_name['ClubNotify'] = _CLUBNOTIFY
DESCRIPTOR.message_types_by_name['CreateClubRequest'] = _CREATECLUBREQUEST
DESCRIPTOR.message_types_by_name['CreateClubResponse'] = _CREATECLUBRESPONSE

class Club(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CLUB

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.club.Club)

class ClubNotify(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CLUBNOTIFY

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.club.ClubNotify)

class CreateClubRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CREATECLUBREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.club.CreateClubRequest)

class CreateClubResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CREATECLUBRESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.club.CreateClubResponse)


# @@protoc_insertion_point(module_scope)