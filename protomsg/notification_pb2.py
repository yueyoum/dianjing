# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: notification.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import common_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='notification.proto',
  package='Dianjing.protocol',
  serialized_pb='\n\x12notification.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\"W\n\x0cNotification\x12\n\n\x02id\x18\x01 \x02(\t\x12\x11\n\ttimestamp\x18\x02 \x02(\x03\x12\n\n\x02tp\x18\x03 \x02(\x05\x12\x0c\n\x04\x61rgs\x18\x04 \x03(\t\x12\x0e\n\x06opened\x18\x05 \x02(\x08\"\x85\x01\n\x12NotificationNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12&\n\x03\x61\x63t\x18\x02 \x02(\x0e\x32\x19.Dianjing.protocol.Action\x12\x36\n\rnotifications\x18\x03 \x03(\x0b\x32\x1f.Dianjing.protocol.Notification\"8\n\x18NotificationRemoveNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0b\n\x03ids\x18\x02 \x03(\t\"6\n\x17NotificationOpenRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\t\"8\n\x18NotificationOpenResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"8\n\x19NotificationDeleteRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\t\":\n\x1aNotificationDeleteResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c')




_NOTIFICATION = _descriptor.Descriptor(
  name='Notification',
  full_name='Dianjing.protocol.Notification',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.Notification.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='Dianjing.protocol.Notification.timestamp', index=1,
      number=2, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tp', full_name='Dianjing.protocol.Notification.tp', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='args', full_name='Dianjing.protocol.Notification.args', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='opened', full_name='Dianjing.protocol.Notification.opened', index=4,
      number=5, type=8, cpp_type=7, label=2,
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
  serialized_start=55,
  serialized_end=142,
)


_NOTIFICATIONNOTIFY = _descriptor.Descriptor(
  name='NotificationNotify',
  full_name='Dianjing.protocol.NotificationNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.NotificationNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='act', full_name='Dianjing.protocol.NotificationNotify.act', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='notifications', full_name='Dianjing.protocol.NotificationNotify.notifications', index=2,
      number=3, type=11, cpp_type=10, label=3,
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
  serialized_start=145,
  serialized_end=278,
)


_NOTIFICATIONREMOVENOTIFY = _descriptor.Descriptor(
  name='NotificationRemoveNotify',
  full_name='Dianjing.protocol.NotificationRemoveNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.NotificationRemoveNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ids', full_name='Dianjing.protocol.NotificationRemoveNotify.ids', index=1,
      number=2, type=9, cpp_type=9, label=3,
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
  serialized_start=280,
  serialized_end=336,
)


_NOTIFICATIONOPENREQUEST = _descriptor.Descriptor(
  name='NotificationOpenRequest',
  full_name='Dianjing.protocol.NotificationOpenRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.NotificationOpenRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.NotificationOpenRequest.id', index=1,
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
  serialized_start=338,
  serialized_end=392,
)


_NOTIFICATIONOPENRESPONSE = _descriptor.Descriptor(
  name='NotificationOpenResponse',
  full_name='Dianjing.protocol.NotificationOpenResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.NotificationOpenResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.NotificationOpenResponse.session', index=1,
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
  serialized_start=394,
  serialized_end=450,
)


_NOTIFICATIONDELETEREQUEST = _descriptor.Descriptor(
  name='NotificationDeleteRequest',
  full_name='Dianjing.protocol.NotificationDeleteRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.NotificationDeleteRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.NotificationDeleteRequest.id', index=1,
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
  serialized_start=452,
  serialized_end=508,
)


_NOTIFICATIONDELETERESPONSE = _descriptor.Descriptor(
  name='NotificationDeleteResponse',
  full_name='Dianjing.protocol.NotificationDeleteResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.NotificationDeleteResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.NotificationDeleteResponse.session', index=1,
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
  serialized_start=510,
  serialized_end=568,
)

_NOTIFICATIONNOTIFY.fields_by_name['act'].enum_type = common_pb2._ACTION
_NOTIFICATIONNOTIFY.fields_by_name['notifications'].message_type = _NOTIFICATION
DESCRIPTOR.message_types_by_name['Notification'] = _NOTIFICATION
DESCRIPTOR.message_types_by_name['NotificationNotify'] = _NOTIFICATIONNOTIFY
DESCRIPTOR.message_types_by_name['NotificationRemoveNotify'] = _NOTIFICATIONREMOVENOTIFY
DESCRIPTOR.message_types_by_name['NotificationOpenRequest'] = _NOTIFICATIONOPENREQUEST
DESCRIPTOR.message_types_by_name['NotificationOpenResponse'] = _NOTIFICATIONOPENRESPONSE
DESCRIPTOR.message_types_by_name['NotificationDeleteRequest'] = _NOTIFICATIONDELETEREQUEST
DESCRIPTOR.message_types_by_name['NotificationDeleteResponse'] = _NOTIFICATIONDELETERESPONSE

class Notification(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NOTIFICATION

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Notification)

class NotificationNotify(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NOTIFICATIONNOTIFY

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.NotificationNotify)

class NotificationRemoveNotify(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NOTIFICATIONREMOVENOTIFY

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.NotificationRemoveNotify)

class NotificationOpenRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NOTIFICATIONOPENREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.NotificationOpenRequest)

class NotificationOpenResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NOTIFICATIONOPENRESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.NotificationOpenResponse)

class NotificationDeleteRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NOTIFICATIONDELETEREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.NotificationDeleteRequest)

class NotificationDeleteResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NOTIFICATIONDELETERESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.NotificationDeleteResponse)


# @@protoc_insertion_point(module_scope)
