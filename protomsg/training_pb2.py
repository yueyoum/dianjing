# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: training.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import common_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='training.proto',
  package='Dianjing.protocol',
  serialized_pb='\n\x0etraining.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\"&\n\x08Training\x12\n\n\x02id\x18\x01 \x02(\x05\x12\x0e\n\x06\x61mount\x18\x02 \x02(\x05\"y\n\x0eTrainingNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12&\n\x03\x61\x63t\x18\x02 \x02(\x0e\x32\x19.Dianjing.protocol.Action\x12.\n\ttrainings\x18\x03 \x03(\x0b\x32\x1b.Dianjing.protocol.Training\"4\n\x14TrainingRemoveNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0b\n\x03ids\x18\x02 \x03(\x05\"1\n\x12TrainingBuyRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\x05\"3\n\x13TrainingBuyResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c')




_TRAINING = _descriptor.Descriptor(
  name='Training',
  full_name='Dianjing.protocol.Training',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.Training.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='amount', full_name='Dianjing.protocol.Training.amount', index=1,
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
  serialized_start=51,
  serialized_end=89,
)


_TRAININGNOTIFY = _descriptor.Descriptor(
  name='TrainingNotify',
  full_name='Dianjing.protocol.TrainingNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TrainingNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='act', full_name='Dianjing.protocol.TrainingNotify.act', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='trainings', full_name='Dianjing.protocol.TrainingNotify.trainings', index=2,
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
  serialized_start=91,
  serialized_end=212,
)


_TRAININGREMOVENOTIFY = _descriptor.Descriptor(
  name='TrainingRemoveNotify',
  full_name='Dianjing.protocol.TrainingRemoveNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TrainingRemoveNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ids', full_name='Dianjing.protocol.TrainingRemoveNotify.ids', index=1,
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
  extension_ranges=[],
  serialized_start=214,
  serialized_end=266,
)


_TRAININGBUYREQUEST = _descriptor.Descriptor(
  name='TrainingBuyRequest',
  full_name='Dianjing.protocol.TrainingBuyRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TrainingBuyRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.TrainingBuyRequest.id', index=1,
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
  serialized_start=268,
  serialized_end=317,
)


_TRAININGBUYRESPONSE = _descriptor.Descriptor(
  name='TrainingBuyResponse',
  full_name='Dianjing.protocol.TrainingBuyResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.TrainingBuyResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TrainingBuyResponse.session', index=1,
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
  serialized_start=319,
  serialized_end=370,
)

_TRAININGNOTIFY.fields_by_name['act'].enum_type = common_pb2._ACTION
_TRAININGNOTIFY.fields_by_name['trainings'].message_type = _TRAINING
DESCRIPTOR.message_types_by_name['Training'] = _TRAINING
DESCRIPTOR.message_types_by_name['TrainingNotify'] = _TRAININGNOTIFY
DESCRIPTOR.message_types_by_name['TrainingRemoveNotify'] = _TRAININGREMOVENOTIFY
DESCRIPTOR.message_types_by_name['TrainingBuyRequest'] = _TRAININGBUYREQUEST
DESCRIPTOR.message_types_by_name['TrainingBuyResponse'] = _TRAININGBUYRESPONSE

class Training(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TRAINING

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Training)

class TrainingNotify(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TRAININGNOTIFY

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TrainingNotify)

class TrainingRemoveNotify(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TRAININGREMOVENOTIFY

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TrainingRemoveNotify)

class TrainingBuyRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TRAININGBUYREQUEST

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TrainingBuyRequest)

class TrainingBuyResponse(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TRAININGBUYRESPONSE

  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TrainingBuyResponse)


# @@protoc_insertion_point(module_scope)