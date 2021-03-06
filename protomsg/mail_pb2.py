# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mail.proto

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


import club_pb2 as club__pb2
import common_pb2 as common__pb2
import package_pb2 as package__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='mail.proto',
  package='Dianjing.protocol',
  syntax='proto2',
  serialized_pb=_b('\n\nmail.proto\x12\x11\x44ianjing.protocol\x1a\nclub.proto\x1a\x0c\x63ommon.proto\x1a\rpackage.proto\"e\n\x08MailFrom\x12\x32\n\tfrom_type\x18\x01 \x02(\x0e\x32\x1f.Dianjing.protocol.MailFromType\x12%\n\x04\x63lub\x18\x02 \x01(\x0b\x32\x17.Dianjing.protocol.Club\"\xa3\x02\n\x04Mail\x12\n\n\x02id\x18\x01 \x02(\t\x12.\n\tmail_from\x18\x02 \x02(\x0b\x32\x1b.Dianjing.protocol.MailFrom\x12\r\n\x05title\x18\x03 \x02(\t\x12\x0f\n\x07\x63ontent\x18\x04 \x02(\t\x12\x10\n\x08has_read\x18\x05 \x02(\x08\x12\x11\n\tcreate_at\x18\x06 \x02(\x03\x12\x18\n\x10remained_seconds\x18\x07 \x02(\x05\x12+\n\nattachment\x18\x08 \x01(\x0b\x32\x17.Dianjing.protocol.Drop\x12\x45\n\x08\x66unction\x18\t \x01(\x0e\x32\x1f.Dianjing.protocol.MailFunction:\x12MAIL_FUNCTION_NONE\x12\x0c\n\x04\x64\x61ta\x18\n \x01(\x0c\"m\n\nMailNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12&\n\x03\x61\x63t\x18\x02 \x02(\x0e\x32\x19.Dianjing.protocol.Action\x12&\n\x05mails\x18\x03 \x03(\x0b\x32\x17.Dianjing.protocol.Mail\"0\n\x10MailRemoveNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0b\n\x03ids\x18\x02 \x03(\t\"B\n\x0fMailSendRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\r\n\x05to_id\x18\x02 \x02(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x02(\t\"0\n\x10MailSendResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\".\n\x0fMailOpenRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\t\"0\n\x10MailOpenResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"0\n\x11MailDeleteRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\t\"2\n\x12MailDeleteResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"7\n\x18MailGetAttachmentRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\t\"f\n\x19MailGetAttachmentResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12+\n\nattachment\x18\x03 \x01(\x0b\x32\x17.Dianjing.protocol.Drop*8\n\x0cMailFromType\x12\x14\n\x10MAIL_FROM_SYSTEM\x10\x01\x12\x12\n\x0eMAIL_FROM_USER\x10\x02*?\n\x0cMailFunction\x12\x16\n\x12MAIL_FUNCTION_NONE\x10\x00\x12\x17\n\x13MAIL_FUNCTION_VIDEO\x10\x01')
  ,
  dependencies=[club__pb2.DESCRIPTOR,common__pb2.DESCRIPTOR,package__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_MAILFROMTYPE = _descriptor.EnumDescriptor(
  name='MailFromType',
  full_name='Dianjing.protocol.MailFromType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='MAIL_FROM_SYSTEM', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MAIL_FROM_USER', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1111,
  serialized_end=1167,
)
_sym_db.RegisterEnumDescriptor(_MAILFROMTYPE)

MailFromType = enum_type_wrapper.EnumTypeWrapper(_MAILFROMTYPE)
_MAILFUNCTION = _descriptor.EnumDescriptor(
  name='MailFunction',
  full_name='Dianjing.protocol.MailFunction',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='MAIL_FUNCTION_NONE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MAIL_FUNCTION_VIDEO', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1169,
  serialized_end=1232,
)
_sym_db.RegisterEnumDescriptor(_MAILFUNCTION)

MailFunction = enum_type_wrapper.EnumTypeWrapper(_MAILFUNCTION)
MAIL_FROM_SYSTEM = 1
MAIL_FROM_USER = 2
MAIL_FUNCTION_NONE = 0
MAIL_FUNCTION_VIDEO = 1



_MAILFROM = _descriptor.Descriptor(
  name='MailFrom',
  full_name='Dianjing.protocol.MailFrom',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='from_type', full_name='Dianjing.protocol.MailFrom.from_type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='club', full_name='Dianjing.protocol.MailFrom.club', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
  serialized_start=74,
  serialized_end=175,
)


_MAIL = _descriptor.Descriptor(
  name='Mail',
  full_name='Dianjing.protocol.Mail',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.Mail.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mail_from', full_name='Dianjing.protocol.Mail.mail_from', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='title', full_name='Dianjing.protocol.Mail.title', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='Dianjing.protocol.Mail.content', index=3,
      number=4, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='has_read', full_name='Dianjing.protocol.Mail.has_read', index=4,
      number=5, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='create_at', full_name='Dianjing.protocol.Mail.create_at', index=5,
      number=6, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='remained_seconds', full_name='Dianjing.protocol.Mail.remained_seconds', index=6,
      number=7, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='attachment', full_name='Dianjing.protocol.Mail.attachment', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='function', full_name='Dianjing.protocol.Mail.function', index=8,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data', full_name='Dianjing.protocol.Mail.data', index=9,
      number=10, type=12, cpp_type=9, label=1,
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
  serialized_start=178,
  serialized_end=469,
)


_MAILNOTIFY = _descriptor.Descriptor(
  name='MailNotify',
  full_name='Dianjing.protocol.MailNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='act', full_name='Dianjing.protocol.MailNotify.act', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mails', full_name='Dianjing.protocol.MailNotify.mails', index=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=471,
  serialized_end=580,
)


_MAILREMOVENOTIFY = _descriptor.Descriptor(
  name='MailRemoveNotify',
  full_name='Dianjing.protocol.MailRemoveNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailRemoveNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ids', full_name='Dianjing.protocol.MailRemoveNotify.ids', index=1,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=582,
  serialized_end=630,
)


_MAILSENDREQUEST = _descriptor.Descriptor(
  name='MailSendRequest',
  full_name='Dianjing.protocol.MailSendRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailSendRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='to_id', full_name='Dianjing.protocol.MailSendRequest.to_id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='Dianjing.protocol.MailSendRequest.content', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=632,
  serialized_end=698,
)


_MAILSENDRESPONSE = _descriptor.Descriptor(
  name='MailSendResponse',
  full_name='Dianjing.protocol.MailSendResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.MailSendResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailSendResponse.session', index=1,
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
  serialized_start=700,
  serialized_end=748,
)


_MAILOPENREQUEST = _descriptor.Descriptor(
  name='MailOpenRequest',
  full_name='Dianjing.protocol.MailOpenRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailOpenRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.MailOpenRequest.id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=750,
  serialized_end=796,
)


_MAILOPENRESPONSE = _descriptor.Descriptor(
  name='MailOpenResponse',
  full_name='Dianjing.protocol.MailOpenResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.MailOpenResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailOpenResponse.session', index=1,
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
  serialized_start=798,
  serialized_end=846,
)


_MAILDELETEREQUEST = _descriptor.Descriptor(
  name='MailDeleteRequest',
  full_name='Dianjing.protocol.MailDeleteRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailDeleteRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.MailDeleteRequest.id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=848,
  serialized_end=896,
)


_MAILDELETERESPONSE = _descriptor.Descriptor(
  name='MailDeleteResponse',
  full_name='Dianjing.protocol.MailDeleteResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.MailDeleteResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailDeleteResponse.session', index=1,
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
  serialized_start=898,
  serialized_end=948,
)


_MAILGETATTACHMENTREQUEST = _descriptor.Descriptor(
  name='MailGetAttachmentRequest',
  full_name='Dianjing.protocol.MailGetAttachmentRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailGetAttachmentRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.MailGetAttachmentRequest.id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=950,
  serialized_end=1005,
)


_MAILGETATTACHMENTRESPONSE = _descriptor.Descriptor(
  name='MailGetAttachmentResponse',
  full_name='Dianjing.protocol.MailGetAttachmentResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.MailGetAttachmentResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.MailGetAttachmentResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='attachment', full_name='Dianjing.protocol.MailGetAttachmentResponse.attachment', index=2,
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
  serialized_start=1007,
  serialized_end=1109,
)

_MAILFROM.fields_by_name['from_type'].enum_type = _MAILFROMTYPE
_MAILFROM.fields_by_name['club'].message_type = club__pb2._CLUB
_MAIL.fields_by_name['mail_from'].message_type = _MAILFROM
_MAIL.fields_by_name['attachment'].message_type = package__pb2._DROP
_MAIL.fields_by_name['function'].enum_type = _MAILFUNCTION
_MAILNOTIFY.fields_by_name['act'].enum_type = common__pb2._ACTION
_MAILNOTIFY.fields_by_name['mails'].message_type = _MAIL
_MAILGETATTACHMENTRESPONSE.fields_by_name['attachment'].message_type = package__pb2._DROP
DESCRIPTOR.message_types_by_name['MailFrom'] = _MAILFROM
DESCRIPTOR.message_types_by_name['Mail'] = _MAIL
DESCRIPTOR.message_types_by_name['MailNotify'] = _MAILNOTIFY
DESCRIPTOR.message_types_by_name['MailRemoveNotify'] = _MAILREMOVENOTIFY
DESCRIPTOR.message_types_by_name['MailSendRequest'] = _MAILSENDREQUEST
DESCRIPTOR.message_types_by_name['MailSendResponse'] = _MAILSENDRESPONSE
DESCRIPTOR.message_types_by_name['MailOpenRequest'] = _MAILOPENREQUEST
DESCRIPTOR.message_types_by_name['MailOpenResponse'] = _MAILOPENRESPONSE
DESCRIPTOR.message_types_by_name['MailDeleteRequest'] = _MAILDELETEREQUEST
DESCRIPTOR.message_types_by_name['MailDeleteResponse'] = _MAILDELETERESPONSE
DESCRIPTOR.message_types_by_name['MailGetAttachmentRequest'] = _MAILGETATTACHMENTREQUEST
DESCRIPTOR.message_types_by_name['MailGetAttachmentResponse'] = _MAILGETATTACHMENTRESPONSE
DESCRIPTOR.enum_types_by_name['MailFromType'] = _MAILFROMTYPE
DESCRIPTOR.enum_types_by_name['MailFunction'] = _MAILFUNCTION

MailFrom = _reflection.GeneratedProtocolMessageType('MailFrom', (_message.Message,), dict(
  DESCRIPTOR = _MAILFROM,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailFrom)
  ))
_sym_db.RegisterMessage(MailFrom)

Mail = _reflection.GeneratedProtocolMessageType('Mail', (_message.Message,), dict(
  DESCRIPTOR = _MAIL,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Mail)
  ))
_sym_db.RegisterMessage(Mail)

MailNotify = _reflection.GeneratedProtocolMessageType('MailNotify', (_message.Message,), dict(
  DESCRIPTOR = _MAILNOTIFY,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailNotify)
  ))
_sym_db.RegisterMessage(MailNotify)

MailRemoveNotify = _reflection.GeneratedProtocolMessageType('MailRemoveNotify', (_message.Message,), dict(
  DESCRIPTOR = _MAILREMOVENOTIFY,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailRemoveNotify)
  ))
_sym_db.RegisterMessage(MailRemoveNotify)

MailSendRequest = _reflection.GeneratedProtocolMessageType('MailSendRequest', (_message.Message,), dict(
  DESCRIPTOR = _MAILSENDREQUEST,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailSendRequest)
  ))
_sym_db.RegisterMessage(MailSendRequest)

MailSendResponse = _reflection.GeneratedProtocolMessageType('MailSendResponse', (_message.Message,), dict(
  DESCRIPTOR = _MAILSENDRESPONSE,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailSendResponse)
  ))
_sym_db.RegisterMessage(MailSendResponse)

MailOpenRequest = _reflection.GeneratedProtocolMessageType('MailOpenRequest', (_message.Message,), dict(
  DESCRIPTOR = _MAILOPENREQUEST,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailOpenRequest)
  ))
_sym_db.RegisterMessage(MailOpenRequest)

MailOpenResponse = _reflection.GeneratedProtocolMessageType('MailOpenResponse', (_message.Message,), dict(
  DESCRIPTOR = _MAILOPENRESPONSE,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailOpenResponse)
  ))
_sym_db.RegisterMessage(MailOpenResponse)

MailDeleteRequest = _reflection.GeneratedProtocolMessageType('MailDeleteRequest', (_message.Message,), dict(
  DESCRIPTOR = _MAILDELETEREQUEST,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailDeleteRequest)
  ))
_sym_db.RegisterMessage(MailDeleteRequest)

MailDeleteResponse = _reflection.GeneratedProtocolMessageType('MailDeleteResponse', (_message.Message,), dict(
  DESCRIPTOR = _MAILDELETERESPONSE,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailDeleteResponse)
  ))
_sym_db.RegisterMessage(MailDeleteResponse)

MailGetAttachmentRequest = _reflection.GeneratedProtocolMessageType('MailGetAttachmentRequest', (_message.Message,), dict(
  DESCRIPTOR = _MAILGETATTACHMENTREQUEST,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailGetAttachmentRequest)
  ))
_sym_db.RegisterMessage(MailGetAttachmentRequest)

MailGetAttachmentResponse = _reflection.GeneratedProtocolMessageType('MailGetAttachmentResponse', (_message.Message,), dict(
  DESCRIPTOR = _MAILGETATTACHMENTRESPONSE,
  __module__ = 'mail_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.MailGetAttachmentResponse)
  ))
_sym_db.RegisterMessage(MailGetAttachmentResponse)


# @@protoc_insertion_point(module_scope)
