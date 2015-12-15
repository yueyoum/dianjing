# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: package.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='package.proto',
  package='Dianjing.protocol',
  syntax='proto2',
  serialized_pb=_b('\n\rpackage.proto\x12\x11\x44ianjing.protocol\".\n\x08Resource\x12\x13\n\x0bresource_id\x18\x01 \x02(\t\x12\r\n\x05value\x18\x02 \x02(\x05\"\xee\x01\n\x04\x44rop\x12.\n\tresources\x18\x01 \x03(\x0b\x32\x1b.Dianjing.protocol.Resource\x12\x38\n\ttrainings\x18\x02 \x03(\x0b\x32%.Dianjing.protocol.Drop.TrainingSkill\x12+\n\x05items\x18\x03 \x03(\x0b\x32\x1c.Dianjing.protocol.Drop.Item\x1a+\n\rTrainingSkill\x12\n\n\x02id\x18\x01 \x02(\x05\x12\x0e\n\x06\x61mount\x18\x02 \x02(\x05\x1a\"\n\x04Item\x12\n\n\x02id\x18\x01 \x02(\x05\x12\x0e\n\x06\x61mount\x18\x02 \x02(\x05\":\n\x08Property\x12.\n\tresources\x18\x01 \x03(\x0b\x32\x1b.Dianjing.protocol.Resource\">\n\x0fItemSellRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\x05\x12\x0e\n\x06\x61mount\x18\x03 \x02(\x05\"0\n\x10ItemSellResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"G\n\x18TrainingSkillSellRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\n\n\x02id\x18\x02 \x02(\x05\x12\x0e\n\x06\x61mount\x18\x03 \x02(\x05\"9\n\x19TrainingSkillSellResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_RESOURCE = _descriptor.Descriptor(
  name='Resource',
  full_name='Dianjing.protocol.Resource',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='resource_id', full_name='Dianjing.protocol.Resource.resource_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='Dianjing.protocol.Resource.value', index=1,
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
  serialized_start=36,
  serialized_end=82,
)


_DROP_TRAININGSKILL = _descriptor.Descriptor(
  name='TrainingSkill',
  full_name='Dianjing.protocol.Drop.TrainingSkill',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.Drop.TrainingSkill.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='amount', full_name='Dianjing.protocol.Drop.TrainingSkill.amount', index=1,
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
  serialized_start=244,
  serialized_end=287,
)

_DROP_ITEM = _descriptor.Descriptor(
  name='Item',
  full_name='Dianjing.protocol.Drop.Item',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.Drop.Item.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='amount', full_name='Dianjing.protocol.Drop.Item.amount', index=1,
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
  serialized_start=289,
  serialized_end=323,
)

_DROP = _descriptor.Descriptor(
  name='Drop',
  full_name='Dianjing.protocol.Drop',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='resources', full_name='Dianjing.protocol.Drop.resources', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='trainings', full_name='Dianjing.protocol.Drop.trainings', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='items', full_name='Dianjing.protocol.Drop.items', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_DROP_TRAININGSKILL, _DROP_ITEM, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=85,
  serialized_end=323,
)


_PROPERTY = _descriptor.Descriptor(
  name='Property',
  full_name='Dianjing.protocol.Property',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='resources', full_name='Dianjing.protocol.Property.resources', index=0,
      number=1, type=11, cpp_type=10, label=3,
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
  serialized_start=325,
  serialized_end=383,
)


_ITEMSELLREQUEST = _descriptor.Descriptor(
  name='ItemSellRequest',
  full_name='Dianjing.protocol.ItemSellRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ItemSellRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.ItemSellRequest.id', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='amount', full_name='Dianjing.protocol.ItemSellRequest.amount', index=2,
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
  serialized_end=447,
)


_ITEMSELLRESPONSE = _descriptor.Descriptor(
  name='ItemSellResponse',
  full_name='Dianjing.protocol.ItemSellResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.ItemSellResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.ItemSellResponse.session', index=1,
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
  serialized_start=449,
  serialized_end=497,
)


_TRAININGSKILLSELLREQUEST = _descriptor.Descriptor(
  name='TrainingSkillSellRequest',
  full_name='Dianjing.protocol.TrainingSkillSellRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TrainingSkillSellRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.TrainingSkillSellRequest.id', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='amount', full_name='Dianjing.protocol.TrainingSkillSellRequest.amount', index=2,
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
  serialized_start=499,
  serialized_end=570,
)


_TRAININGSKILLSELLRESPONSE = _descriptor.Descriptor(
  name='TrainingSkillSellResponse',
  full_name='Dianjing.protocol.TrainingSkillSellResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.TrainingSkillSellResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TrainingSkillSellResponse.session', index=1,
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
  serialized_start=572,
  serialized_end=629,
)

_DROP_TRAININGSKILL.containing_type = _DROP
_DROP_ITEM.containing_type = _DROP
_DROP.fields_by_name['resources'].message_type = _RESOURCE
_DROP.fields_by_name['trainings'].message_type = _DROP_TRAININGSKILL
_DROP.fields_by_name['items'].message_type = _DROP_ITEM
_PROPERTY.fields_by_name['resources'].message_type = _RESOURCE
DESCRIPTOR.message_types_by_name['Resource'] = _RESOURCE
DESCRIPTOR.message_types_by_name['Drop'] = _DROP
DESCRIPTOR.message_types_by_name['Property'] = _PROPERTY
DESCRIPTOR.message_types_by_name['ItemSellRequest'] = _ITEMSELLREQUEST
DESCRIPTOR.message_types_by_name['ItemSellResponse'] = _ITEMSELLRESPONSE
DESCRIPTOR.message_types_by_name['TrainingSkillSellRequest'] = _TRAININGSKILLSELLREQUEST
DESCRIPTOR.message_types_by_name['TrainingSkillSellResponse'] = _TRAININGSKILLSELLRESPONSE

Resource = _reflection.GeneratedProtocolMessageType('Resource', (_message.Message,), dict(
  DESCRIPTOR = _RESOURCE,
  __module__ = 'package_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Resource)
  ))
_sym_db.RegisterMessage(Resource)

Drop = _reflection.GeneratedProtocolMessageType('Drop', (_message.Message,), dict(

  TrainingSkill = _reflection.GeneratedProtocolMessageType('TrainingSkill', (_message.Message,), dict(
    DESCRIPTOR = _DROP_TRAININGSKILL,
    __module__ = 'package_pb2'
    # @@protoc_insertion_point(class_scope:Dianjing.protocol.Drop.TrainingSkill)
    ))
  ,

  Item = _reflection.GeneratedProtocolMessageType('Item', (_message.Message,), dict(
    DESCRIPTOR = _DROP_ITEM,
    __module__ = 'package_pb2'
    # @@protoc_insertion_point(class_scope:Dianjing.protocol.Drop.Item)
    ))
  ,
  DESCRIPTOR = _DROP,
  __module__ = 'package_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Drop)
  ))
_sym_db.RegisterMessage(Drop)
_sym_db.RegisterMessage(Drop.TrainingSkill)
_sym_db.RegisterMessage(Drop.Item)

Property = _reflection.GeneratedProtocolMessageType('Property', (_message.Message,), dict(
  DESCRIPTOR = _PROPERTY,
  __module__ = 'package_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Property)
  ))
_sym_db.RegisterMessage(Property)

ItemSellRequest = _reflection.GeneratedProtocolMessageType('ItemSellRequest', (_message.Message,), dict(
  DESCRIPTOR = _ITEMSELLREQUEST,
  __module__ = 'package_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ItemSellRequest)
  ))
_sym_db.RegisterMessage(ItemSellRequest)

ItemSellResponse = _reflection.GeneratedProtocolMessageType('ItemSellResponse', (_message.Message,), dict(
  DESCRIPTOR = _ITEMSELLRESPONSE,
  __module__ = 'package_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.ItemSellResponse)
  ))
_sym_db.RegisterMessage(ItemSellResponse)

TrainingSkillSellRequest = _reflection.GeneratedProtocolMessageType('TrainingSkillSellRequest', (_message.Message,), dict(
  DESCRIPTOR = _TRAININGSKILLSELLREQUEST,
  __module__ = 'package_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TrainingSkillSellRequest)
  ))
_sym_db.RegisterMessage(TrainingSkillSellRequest)

TrainingSkillSellResponse = _reflection.GeneratedProtocolMessageType('TrainingSkillSellResponse', (_message.Message,), dict(
  DESCRIPTOR = _TRAININGSKILLSELLRESPONSE,
  __module__ = 'package_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TrainingSkillSellResponse)
  ))
_sym_db.RegisterMessage(TrainingSkillSellResponse)


# @@protoc_insertion_point(module_scope)
