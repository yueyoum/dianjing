# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: activity.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import common_pb2 as common__pb2
import package_pb2 as package__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='activity.proto',
  package='Dianjing.protocol',
  syntax='proto2',
  serialized_pb=_b('\n\x0e\x61\x63tivity.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\x1a\rpackage.proto\"\xb2\x02\n\x17\x41\x63tivityNewPlayerNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12&\n\x03\x61\x63t\x18\x02 \x02(\x0e\x32\x19.Dianjing.protocol.Action\x12G\n\x05items\x18\x03 \x03(\x0b\x32\x38.Dianjing.protocol.ActivityNewPlayerNotify.NewPlayerItem\x12\x17\n\x0f\x61\x63tivity_end_at\x18\x04 \x02(\x03\x12\x15\n\rreward_end_at\x18\x05 \x02(\x03\x1a\x65\n\rNewPlayerItem\x12\n\n\x02id\x18\x01 \x02(\x05\x12\x15\n\rcurrent_value\x18\x02 \x02(\x05\x12\x31\n\x06status\x18\x03 \x02(\x0e\x32!.Dianjing.protocol.ActivityStatus\"\xb8\x01\n\x1f\x41\x63tivityNewPlayerDailyBuyNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12Q\n\x06status\x18\x02 \x03(\x0b\x32\x41.Dianjing.protocol.ActivityNewPlayerDailyBuyNotify.DailyBuyStatus\x1a\x31\n\x0e\x44\x61ilyBuyStatus\x12\x0b\n\x03\x64\x61y\x18\x01 \x02(\x05\x12\x12\n\nhas_bought\x18\x02 \x02(\x08\"@\n!ActivityNewPlayerGetRewardRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\x05\"i\n\"ActivityNewPlayerGetRewardResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12%\n\x04\x64rop\x18\x03 \x01(\x0b\x32\x17.Dianjing.protocol.Drop\"3\n ActivityNewPlayerDailyBuyRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\"h\n!ActivityNewPlayerDailyBuyResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12%\n\x04\x64rop\x18\x03 \x01(\x0b\x32\x17.Dianjing.protocol.Drop*P\n\x0e\x41\x63tivityStatus\x12\x12\n\x0e\x41\x43TIVITY_DOING\x10\x01\x12\x13\n\x0f\x41\x43TIVITY_REWARD\x10\x02\x12\x15\n\x11\x41\x43TIVITY_COMPLETE\x10\x03')
  ,
  dependencies=[common__pb2.DESCRIPTOR,package__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_ACTIVITYSTATUS = _descriptor.EnumDescriptor(
  name='ActivityStatus',
  full_name='Dianjing.protocol.ActivityStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ACTIVITY_DOING', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ACTIVITY_REWARD', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ACTIVITY_COMPLETE', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=894,
  serialized_end=974,
)
_sym_db.RegisterEnumDescriptor(_ACTIVITYSTATUS)

ActivityStatus = enum_type_wrapper.EnumTypeWrapper(_ACTIVITYSTATUS)
ACTIVITY_DOING = 1
ACTIVITY_REWARD = 2
ACTIVITY_COMPLETE = 3



_ACTIVITYNEWPLAYERNOTIFY_NEWPLAYERITEM = _descriptor.Descriptor(
  name='NewPlayerItem',
  full_name='Dianjing.protocol.ActivityNewPlayerNotify.NewPlayerItem',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.ActivityNewPlayerNotify.NewPlayerItem.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='current_value', full_name='Dianjing.protocol.ActivityNewPlayerNotify.NewPlayerItem.current_value', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='Dianjing.protocol.ActivityNewPlayerNotify.NewPlayerItem.status', index=2,
      number=3, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
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
  serialized_start=272,
  serialized_end=373,
)

_ACTIVITYNEWPLAYERNOTIFY = _descriptor.Descriptor(
  name='ActivityNewPlayerNotify',
  full_name='Dianjing.protocol.ActivityNewPlayerNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ActivityNewPlayerNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='act', full_name='Dianjing.protocol.ActivityNewPlayerNotify.act', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='items', full_name='Dianjing.protocol.ActivityNewPlayerNotify.items', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='activity_end_at', full_name='Dianjing.protocol.ActivityNewPlayerNotify.activity_end_at', index=3,
      number=4, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='reward_end_at', full_name='Dianjing.protocol.ActivityNewPlayerNotify.reward_end_at', index=4,
      number=5, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_ACTIVITYNEWPLAYERNOTIFY_NEWPLAYERITEM, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=67,
  serialized_end=373,
)


_ACTIVITYNEWPLAYERDAILYBUYNOTIFY_DAILYBUYSTATUS = _descriptor.Descriptor(
  name='DailyBuyStatus',
  full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyNotify.DailyBuyStatus',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='day', full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyNotify.DailyBuyStatus.day', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='has_bought', full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyNotify.DailyBuyStatus.has_bought', index=1,
      number=2, type=8, cpp_type=7, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=511,
  serialized_end=560,
)

_ACTIVITYNEWPLAYERDAILYBUYNOTIFY = _descriptor.Descriptor(
  name='ActivityNewPlayerDailyBuyNotify',
  full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyNotify.status', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_ACTIVITYNEWPLAYERDAILYBUYNOTIFY_DAILYBUYSTATUS, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=376,
  serialized_end=560,
)


_ACTIVITYNEWPLAYERGETREWARDREQUEST = _descriptor.Descriptor(
  name='ActivityNewPlayerGetRewardRequest',
  full_name='Dianjing.protocol.ActivityNewPlayerGetRewardRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ActivityNewPlayerGetRewardRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.ActivityNewPlayerGetRewardRequest.id', index=1,
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
  serialized_start=562,
  serialized_end=626,
)


_ACTIVITYNEWPLAYERGETREWARDRESPONSE = _descriptor.Descriptor(
  name='ActivityNewPlayerGetRewardResponse',
  full_name='Dianjing.protocol.ActivityNewPlayerGetRewardResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.ActivityNewPlayerGetRewardResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ActivityNewPlayerGetRewardResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='drop', full_name='Dianjing.protocol.ActivityNewPlayerGetRewardResponse.drop', index=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=628,
  serialized_end=733,
)


_ACTIVITYNEWPLAYERDAILYBUYREQUEST = _descriptor.Descriptor(
  name='ActivityNewPlayerDailyBuyRequest',
  full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyRequest.session', index=0,
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
  serialized_start=735,
  serialized_end=786,
)


_ACTIVITYNEWPLAYERDAILYBUYRESPONSE = _descriptor.Descriptor(
  name='ActivityNewPlayerDailyBuyResponse',
  full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='drop', full_name='Dianjing.protocol.ActivityNewPlayerDailyBuyResponse.drop', index=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=788,
  serialized_end=892,
)

_ACTIVITYNEWPLAYERNOTIFY_NEWPLAYERITEM.fields_by_name['status'].enum_type = _ACTIVITYSTATUS
_ACTIVITYNEWPLAYERNOTIFY_NEWPLAYERITEM.containing_type = _ACTIVITYNEWPLAYERNOTIFY
_ACTIVITYNEWPLAYERNOTIFY.fields_by_name['act'].enum_type = common__pb2._ACTION
_ACTIVITYNEWPLAYERNOTIFY.fields_by_name['items'].message_type = _ACTIVITYNEWPLAYERNOTIFY_NEWPLAYERITEM
_ACTIVITYNEWPLAYERDAILYBUYNOTIFY_DAILYBUYSTATUS.containing_type = _ACTIVITYNEWPLAYERDAILYBUYNOTIFY
_ACTIVITYNEWPLAYERDAILYBUYNOTIFY.fields_by_name['status'].message_type = _ACTIVITYNEWPLAYERDAILYBUYNOTIFY_DAILYBUYSTATUS
_ACTIVITYNEWPLAYERGETREWARDRESPONSE.fields_by_name['drop'].message_type = package__pb2._DROP
_ACTIVITYNEWPLAYERDAILYBUYRESPONSE.fields_by_name['drop'].message_type = package__pb2._DROP
DESCRIPTOR.message_types_by_name['ActivityNewPlayerNotify'] = _ACTIVITYNEWPLAYERNOTIFY
DESCRIPTOR.message_types_by_name['ActivityNewPlayerDailyBuyNotify'] = _ACTIVITYNEWPLAYERDAILYBUYNOTIFY
DESCRIPTOR.message_types_by_name['ActivityNewPlayerGetRewardRequest'] = _ACTIVITYNEWPLAYERGETREWARDREQUEST
DESCRIPTOR.message_types_by_name['ActivityNewPlayerGetRewardResponse'] = _ACTIVITYNEWPLAYERGETREWARDRESPONSE
DESCRIPTOR.message_types_by_name['ActivityNewPlayerDailyBuyRequest'] = _ACTIVITYNEWPLAYERDAILYBUYREQUEST
DESCRIPTOR.message_types_by_name['ActivityNewPlayerDailyBuyResponse'] = _ACTIVITYNEWPLAYERDAILYBUYRESPONSE
DESCRIPTOR.enum_types_by_name['ActivityStatus'] = _ACTIVITYSTATUS

ActivityNewPlayerNotify = _reflection.GeneratedProtocolMessageType('ActivityNewPlayerNotify', (_message.Message,), dict(

  NewPlayerItem = _reflection.GeneratedProtocolMessageType('NewPlayerItem', (_message.Message,), dict(
    DESCRIPTOR = _ACTIVITYNEWPLAYERNOTIFY_NEWPLAYERITEM,
    __module__ = 'activity_pb2'
    # @@protoc_insertion_point(class_scope:Dianjing.protocol.ActivityNewPlayerNotify.NewPlayerItem)
    ))
  ,
  DESCRIPTOR = _ACTIVITYNEWPLAYERNOTIFY,
  __module__ = 'activity_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ActivityNewPlayerNotify)
  ))
_sym_db.RegisterMessage(ActivityNewPlayerNotify)
_sym_db.RegisterMessage(ActivityNewPlayerNotify.NewPlayerItem)

ActivityNewPlayerDailyBuyNotify = _reflection.GeneratedProtocolMessageType('ActivityNewPlayerDailyBuyNotify', (_message.Message,), dict(

  DailyBuyStatus = _reflection.GeneratedProtocolMessageType('DailyBuyStatus', (_message.Message,), dict(
    DESCRIPTOR = _ACTIVITYNEWPLAYERDAILYBUYNOTIFY_DAILYBUYSTATUS,
    __module__ = 'activity_pb2'
    # @@protoc_insertion_point(class_scope:Dianjing.protocol.ActivityNewPlayerDailyBuyNotify.DailyBuyStatus)
    ))
  ,
  DESCRIPTOR = _ACTIVITYNEWPLAYERDAILYBUYNOTIFY,
  __module__ = 'activity_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ActivityNewPlayerDailyBuyNotify)
  ))
_sym_db.RegisterMessage(ActivityNewPlayerDailyBuyNotify)
_sym_db.RegisterMessage(ActivityNewPlayerDailyBuyNotify.DailyBuyStatus)

ActivityNewPlayerGetRewardRequest = _reflection.GeneratedProtocolMessageType('ActivityNewPlayerGetRewardRequest', (_message.Message,), dict(
  DESCRIPTOR = _ACTIVITYNEWPLAYERGETREWARDREQUEST,
  __module__ = 'activity_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ActivityNewPlayerGetRewardRequest)
  ))
_sym_db.RegisterMessage(ActivityNewPlayerGetRewardRequest)

ActivityNewPlayerGetRewardResponse = _reflection.GeneratedProtocolMessageType('ActivityNewPlayerGetRewardResponse', (_message.Message,), dict(
  DESCRIPTOR = _ACTIVITYNEWPLAYERGETREWARDRESPONSE,
  __module__ = 'activity_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ActivityNewPlayerGetRewardResponse)
  ))
_sym_db.RegisterMessage(ActivityNewPlayerGetRewardResponse)

ActivityNewPlayerDailyBuyRequest = _reflection.GeneratedProtocolMessageType('ActivityNewPlayerDailyBuyRequest', (_message.Message,), dict(
  DESCRIPTOR = _ACTIVITYNEWPLAYERDAILYBUYREQUEST,
  __module__ = 'activity_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ActivityNewPlayerDailyBuyRequest)
  ))
_sym_db.RegisterMessage(ActivityNewPlayerDailyBuyRequest)

ActivityNewPlayerDailyBuyResponse = _reflection.GeneratedProtocolMessageType('ActivityNewPlayerDailyBuyResponse', (_message.Message,), dict(
  DESCRIPTOR = _ACTIVITYNEWPLAYERDAILYBUYRESPONSE,
  __module__ = 'activity_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ActivityNewPlayerDailyBuyResponse)
  ))
_sym_db.RegisterMessage(ActivityNewPlayerDailyBuyResponse)


# @@protoc_insertion_point(module_scope)
