# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: club.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import common_pb2 as common__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='club.proto',
  package='Dianjing.protocol',
  syntax='proto2',
  serialized_pb=_b('\n\nclub.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\"8\n\nMatchStaff\x12\n\n\x02id\x18\x01 \x02(\x05\x12\r\n\x05level\x18\x02 \x02(\x05\x12\x0f\n\x07qianban\x18\x03 \x03(\x05\"\xcf\x01\n\x04\x43lub\x12\n\n\x02id\x18\x01 \x02(\t\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x0f\n\x07manager\x18\x03 \x02(\t\x12\x0c\n\x04\x66lag\x18\x04 \x02(\x05\x12\r\n\x05level\x18\x05 \x02(\x05\x12\x0e\n\x06renown\x18\x06 \x02(\x05\x12\x0b\n\x03vip\x18\x07 \x02(\x05\x12\x0c\n\x04gold\x18\x08 \x02(\x05\x12\x0f\n\x07\x64iamond\x18\t \x02(\x05\x12\x33\n\x0cmatch_staffs\x18\n \x03(\x0b\x32\x1d.Dianjing.protocol.MatchStaff\x12\x0e\n\x06policy\x18\x0b \x02(\x05\"D\n\nClubNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12%\n\x04\x63lub\x18\x02 \x02(\x0b\x32\x17.Dianjing.protocol.Club\"@\n\x11\x43reateClubRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x0c\n\x04\x66lag\x18\x03 \x02(\x05\"2\n\x12\x43reateClubResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\":\n\x14\x43lubSetPolicyRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x11\n\tpolicy_id\x18\x02 \x02(\x05\"5\n\x15\x43lubSetPolicyResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\">\n\x18\x43lubSetMatchStaffRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x11\n\tstaff_ids\x18\x02 \x03(\x05\"9\n\x19\x43lubSetMatchStaffResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"S\n\x1a\x43lubStaffSlotsAmountNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0e\n\x06\x61mount\x18\x02 \x02(\x05\x12\x14\n\x0c\x63ost_diamond\x18\x03 \x02(\x05\"*\n\x17\x43lubStaffSlotBuyRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\"8\n\x18\x43lubStaffSlotBuyResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c')
  ,
  dependencies=[common__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_MATCHSTAFF = _descriptor.Descriptor(
  name='MatchStaff',
  full_name='Dianjing.protocol.MatchStaff',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.MatchStaff.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='level', full_name='Dianjing.protocol.MatchStaff.level', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='qianban', full_name='Dianjing.protocol.MatchStaff.qianban', index=2,
      number=3, type=5, cpp_type=1, label=3,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=47,
  serialized_end=103,
)


_CLUB = _descriptor.Descriptor(
  name='Club',
  full_name='Dianjing.protocol.Club',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.Club.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='Dianjing.protocol.Club.name', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='manager', full_name='Dianjing.protocol.Club.manager', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='flag', full_name='Dianjing.protocol.Club.flag', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='level', full_name='Dianjing.protocol.Club.level', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='renown', full_name='Dianjing.protocol.Club.renown', index=5,
      number=6, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='vip', full_name='Dianjing.protocol.Club.vip', index=6,
      number=7, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gold', full_name='Dianjing.protocol.Club.gold', index=7,
      number=8, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='diamond', full_name='Dianjing.protocol.Club.diamond', index=8,
      number=9, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='match_staffs', full_name='Dianjing.protocol.Club.match_staffs', index=9,
      number=10, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='policy', full_name='Dianjing.protocol.Club.policy', index=10,
      number=11, type=5, cpp_type=1, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=106,
  serialized_end=313,
)


_CLUBNOTIFY = _descriptor.Descriptor(
  name='ClubNotify',
  full_name='Dianjing.protocol.ClubNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ClubNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='club', full_name='Dianjing.protocol.ClubNotify.club', index=1,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=315,
  serialized_end=383,
)


_CREATECLUBREQUEST = _descriptor.Descriptor(
  name='CreateClubRequest',
  full_name='Dianjing.protocol.CreateClubRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CreateClubRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='Dianjing.protocol.CreateClubRequest.name', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='flag', full_name='Dianjing.protocol.CreateClubRequest.flag', index=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=385,
  serialized_end=449,
)


_CREATECLUBRESPONSE = _descriptor.Descriptor(
  name='CreateClubResponse',
  full_name='Dianjing.protocol.CreateClubResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.CreateClubResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.CreateClubResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=451,
  serialized_end=501,
)


_CLUBSETPOLICYREQUEST = _descriptor.Descriptor(
  name='ClubSetPolicyRequest',
  full_name='Dianjing.protocol.ClubSetPolicyRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ClubSetPolicyRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='policy_id', full_name='Dianjing.protocol.ClubSetPolicyRequest.policy_id', index=1,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=503,
  serialized_end=561,
)


_CLUBSETPOLICYRESPONSE = _descriptor.Descriptor(
  name='ClubSetPolicyResponse',
  full_name='Dianjing.protocol.ClubSetPolicyResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.ClubSetPolicyResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ClubSetPolicyResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=563,
  serialized_end=616,
)


_CLUBSETMATCHSTAFFREQUEST = _descriptor.Descriptor(
  name='ClubSetMatchStaffRequest',
  full_name='Dianjing.protocol.ClubSetMatchStaffRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ClubSetMatchStaffRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_ids', full_name='Dianjing.protocol.ClubSetMatchStaffRequest.staff_ids', index=1,
      number=2, type=5, cpp_type=1, label=3,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=618,
  serialized_end=680,
)


_CLUBSETMATCHSTAFFRESPONSE = _descriptor.Descriptor(
  name='ClubSetMatchStaffResponse',
  full_name='Dianjing.protocol.ClubSetMatchStaffResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.ClubSetMatchStaffResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ClubSetMatchStaffResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=682,
  serialized_end=739,
)


_CLUBSTAFFSLOTSAMOUNTNOTIFY = _descriptor.Descriptor(
  name='ClubStaffSlotsAmountNotify',
  full_name='Dianjing.protocol.ClubStaffSlotsAmountNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ClubStaffSlotsAmountNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='amount', full_name='Dianjing.protocol.ClubStaffSlotsAmountNotify.amount', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cost_diamond', full_name='Dianjing.protocol.ClubStaffSlotsAmountNotify.cost_diamond', index=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=741,
  serialized_end=824,
)


_CLUBSTAFFSLOTBUYREQUEST = _descriptor.Descriptor(
  name='ClubStaffSlotBuyRequest',
  full_name='Dianjing.protocol.ClubStaffSlotBuyRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ClubStaffSlotBuyRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=826,
  serialized_end=868,
)


_CLUBSTAFFSLOTBUYRESPONSE = _descriptor.Descriptor(
  name='ClubStaffSlotBuyResponse',
  full_name='Dianjing.protocol.ClubStaffSlotBuyResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.ClubStaffSlotBuyResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ClubStaffSlotBuyResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=870,
  serialized_end=926,
)

_CLUB.fields_by_name['match_staffs'].message_type = _MATCHSTAFF
_CLUBNOTIFY.fields_by_name['club'].message_type = _CLUB
DESCRIPTOR.message_types_by_name['MatchStaff'] = _MATCHSTAFF
DESCRIPTOR.message_types_by_name['Club'] = _CLUB
DESCRIPTOR.message_types_by_name['ClubNotify'] = _CLUBNOTIFY
DESCRIPTOR.message_types_by_name['CreateClubRequest'] = _CREATECLUBREQUEST
DESCRIPTOR.message_types_by_name['CreateClubResponse'] = _CREATECLUBRESPONSE
DESCRIPTOR.message_types_by_name['ClubSetPolicyRequest'] = _CLUBSETPOLICYREQUEST
DESCRIPTOR.message_types_by_name['ClubSetPolicyResponse'] = _CLUBSETPOLICYRESPONSE
DESCRIPTOR.message_types_by_name['ClubSetMatchStaffRequest'] = _CLUBSETMATCHSTAFFREQUEST
DESCRIPTOR.message_types_by_name['ClubSetMatchStaffResponse'] = _CLUBSETMATCHSTAFFRESPONSE
DESCRIPTOR.message_types_by_name['ClubStaffSlotsAmountNotify'] = _CLUBSTAFFSLOTSAMOUNTNOTIFY
DESCRIPTOR.message_types_by_name['ClubStaffSlotBuyRequest'] = _CLUBSTAFFSLOTBUYREQUEST
DESCRIPTOR.message_types_by_name['ClubStaffSlotBuyResponse'] = _CLUBSTAFFSLOTBUYRESPONSE

MatchStaff = _reflection.GeneratedProtocolMessageType('MatchStaff', (_message.Message,), dict(
  DESCRIPTOR = _MATCHSTAFF,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MatchStaff)
  ))
_sym_db.RegisterMessage(MatchStaff)

Club = _reflection.GeneratedProtocolMessageType('Club', (_message.Message,), dict(
  DESCRIPTOR = _CLUB,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Club)
  ))
_sym_db.RegisterMessage(Club)

ClubNotify = _reflection.GeneratedProtocolMessageType('ClubNotify', (_message.Message,), dict(
  DESCRIPTOR = _CLUBNOTIFY,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ClubNotify)
  ))
_sym_db.RegisterMessage(ClubNotify)

CreateClubRequest = _reflection.GeneratedProtocolMessageType('CreateClubRequest', (_message.Message,), dict(
  DESCRIPTOR = _CREATECLUBREQUEST,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CreateClubRequest)
  ))
_sym_db.RegisterMessage(CreateClubRequest)

CreateClubResponse = _reflection.GeneratedProtocolMessageType('CreateClubResponse', (_message.Message,), dict(
  DESCRIPTOR = _CREATECLUBRESPONSE,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.CreateClubResponse)
  ))
_sym_db.RegisterMessage(CreateClubResponse)

ClubSetPolicyRequest = _reflection.GeneratedProtocolMessageType('ClubSetPolicyRequest', (_message.Message,), dict(
  DESCRIPTOR = _CLUBSETPOLICYREQUEST,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ClubSetPolicyRequest)
  ))
_sym_db.RegisterMessage(ClubSetPolicyRequest)

ClubSetPolicyResponse = _reflection.GeneratedProtocolMessageType('ClubSetPolicyResponse', (_message.Message,), dict(
  DESCRIPTOR = _CLUBSETPOLICYRESPONSE,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ClubSetPolicyResponse)
  ))
_sym_db.RegisterMessage(ClubSetPolicyResponse)

ClubSetMatchStaffRequest = _reflection.GeneratedProtocolMessageType('ClubSetMatchStaffRequest', (_message.Message,), dict(
  DESCRIPTOR = _CLUBSETMATCHSTAFFREQUEST,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ClubSetMatchStaffRequest)
  ))
_sym_db.RegisterMessage(ClubSetMatchStaffRequest)

ClubSetMatchStaffResponse = _reflection.GeneratedProtocolMessageType('ClubSetMatchStaffResponse', (_message.Message,), dict(
  DESCRIPTOR = _CLUBSETMATCHSTAFFRESPONSE,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ClubSetMatchStaffResponse)
  ))
_sym_db.RegisterMessage(ClubSetMatchStaffResponse)

ClubStaffSlotsAmountNotify = _reflection.GeneratedProtocolMessageType('ClubStaffSlotsAmountNotify', (_message.Message,), dict(
  DESCRIPTOR = _CLUBSTAFFSLOTSAMOUNTNOTIFY,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ClubStaffSlotsAmountNotify)
  ))
_sym_db.RegisterMessage(ClubStaffSlotsAmountNotify)

ClubStaffSlotBuyRequest = _reflection.GeneratedProtocolMessageType('ClubStaffSlotBuyRequest', (_message.Message,), dict(
  DESCRIPTOR = _CLUBSTAFFSLOTBUYREQUEST,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ClubStaffSlotBuyRequest)
  ))
_sym_db.RegisterMessage(ClubStaffSlotBuyRequest)

ClubStaffSlotBuyResponse = _reflection.GeneratedProtocolMessageType('ClubStaffSlotBuyResponse', (_message.Message,), dict(
  DESCRIPTOR = _CLUBSTAFFSLOTBUYRESPONSE,
  __module__ = 'club_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ClubStaffSlotBuyResponse)
  ))
_sym_db.RegisterMessage(ClubStaffSlotBuyResponse)


# @@protoc_insertion_point(module_scope)
