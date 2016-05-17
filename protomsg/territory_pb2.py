# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: territory.proto

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
  name='territory.proto',
  package='Dianjing.protocol',
  syntax='proto2',
  serialized_pb=_b('\n\x0fterritory.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\x1a\rpackage.proto\"\x81\x02\n\rTerritorySlot\x12\n\n\x02id\x18\x01 \x02(\x05\x12\x36\n\x06status\x18\x02 \x02(\x0e\x32&.Dianjing.protocol.TerritorySlotStatus\x12\x10\n\x08staff_id\x18\x03 \x01(\x05\x12\x0c\n\x04hour\x18\x04 \x01(\x05\x12\x0e\n\x06\x65nd_at\x18\x05 \x01(\x03\x12\x0b\n\x03key\x18\x06 \x01(\t\x12\x37\n\x06report\x18\x08 \x03(\x0b\x32\'.Dianjing.protocol.TerritorySlot.Report\x1a\x36\n\x06Report\x12\n\n\x02id\x18\x01 \x02(\x05\x12\r\n\x05param\x18\x02 \x03(\t\x12\x11\n\ttimestamp\x18\x03 \x02(\x03\"\x89\x02\n\x11TerritoryBuilding\x12\n\n\x02id\x18\x01 \x02(\x05\x12:\n\x06status\x18\x02 \x02(\x0e\x32*.Dianjing.protocol.TerritoryBuildingStatus\x12\r\n\x05level\x18\x03 \x01(\x05\x12\x0b\n\x03\x65xp\x18\x04 \x01(\x05\x12\x12\n\nproduct_id\x18\x05 \x01(\x05\x12\x16\n\x0eproduct_amount\x18\x06 \x01(\x05\x12\x14\n\x0cinspire_cost\x18\x07 \x01(\x05\x12\x1d\n\x15remained_inpire_times\x18\x08 \x01(\x05\x12/\n\x05slots\x18\t \x03(\x0b\x32 .Dianjing.protocol.TerritorySlot\"\xae\x01\n\x0fTerritoryNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12&\n\x03\x61\x63t\x18\x02 \x02(\x0e\x32\x19.Dianjing.protocol.Action\x12\x37\n\tbuildings\x18\x03 \x03(\x0b\x32$.Dianjing.protocol.TerritoryBuilding\x12\x16\n\x0etraining_hours\x18\x04 \x03(\x05\x12\x11\n\twork_card\x18\x05 \x02(\x05\"x\n\x1fTerritoryTrainingPrepareRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x13\n\x0b\x62uilding_id\x18\x02 \x02(\x05\x12\x0f\n\x07slot_id\x18\x03 \x02(\x05\x12\x10\n\x08staff_id\x18\x04 \x02(\x05\x12\x0c\n\x04hour\x18\x05 \x02(\x05\"\x86\x01\n TerritoryTrainingPrepareResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12\x0b\n\x03\x65xp\x18\x03 \x01(\x05\x12\x12\n\nproduct_id\x18\x04 \x01(\x05\x12\x16\n\x0eproduct_amount\x18\x05 \x01(\x05\x12\x0b\n\x03key\x18\x06 \x01(\t\"=\n\x1dTerritoryTrainingStartReqeust\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0b\n\x03key\x18\x02 \x02(\t\">\n\x1eTerritoryTrainingStartResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"A\n!TerritoryTrainingGetRewardReqeust\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0b\n\x03key\x18\x02 \x02(\t\"i\n\"TerritoryTrainingGetRewardResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\x12%\n\x04\x64rop\x18\x03 \x01(\x0b\x32\x17.Dianjing.protocol.Drop*S\n\x17TerritoryBuildingStatus\x12\x1b\n\x17TERRITORY_BUILDING_OPEN\x10\x01\x12\x1b\n\x17TERRITORY_BUILDING_LOCK\x10\x02*G\n\x13TerritorySlotStatus\x12\x17\n\x13TERRITORY_SLOT_OPEN\x10\x01\x12\x17\n\x13TERRITORY_SLOT_LOCK\x10\x02')
  ,
  dependencies=[common__pb2.DESCRIPTOR,package__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_TERRITORYBUILDINGSTATUS = _descriptor.EnumDescriptor(
  name='TerritoryBuildingStatus',
  full_name='Dianjing.protocol.TerritoryBuildingStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='TERRITORY_BUILDING_OPEN', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TERRITORY_BUILDING_LOCK', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1332,
  serialized_end=1415,
)
_sym_db.RegisterEnumDescriptor(_TERRITORYBUILDINGSTATUS)

TerritoryBuildingStatus = enum_type_wrapper.EnumTypeWrapper(_TERRITORYBUILDINGSTATUS)
_TERRITORYSLOTSTATUS = _descriptor.EnumDescriptor(
  name='TerritorySlotStatus',
  full_name='Dianjing.protocol.TerritorySlotStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='TERRITORY_SLOT_OPEN', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TERRITORY_SLOT_LOCK', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1417,
  serialized_end=1488,
)
_sym_db.RegisterEnumDescriptor(_TERRITORYSLOTSTATUS)

TerritorySlotStatus = enum_type_wrapper.EnumTypeWrapper(_TERRITORYSLOTSTATUS)
TERRITORY_BUILDING_OPEN = 1
TERRITORY_BUILDING_LOCK = 2
TERRITORY_SLOT_OPEN = 1
TERRITORY_SLOT_LOCK = 2



_TERRITORYSLOT_REPORT = _descriptor.Descriptor(
  name='Report',
  full_name='Dianjing.protocol.TerritorySlot.Report',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.TerritorySlot.Report.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='param', full_name='Dianjing.protocol.TerritorySlot.Report.param', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='Dianjing.protocol.TerritorySlot.Report.timestamp', index=2,
      number=3, type=3, cpp_type=2, label=2,
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
  serialized_start=271,
  serialized_end=325,
)

_TERRITORYSLOT = _descriptor.Descriptor(
  name='TerritorySlot',
  full_name='Dianjing.protocol.TerritorySlot',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.TerritorySlot.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='Dianjing.protocol.TerritorySlot.status', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.TerritorySlot.staff_id', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='hour', full_name='Dianjing.protocol.TerritorySlot.hour', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='end_at', full_name='Dianjing.protocol.TerritorySlot.end_at', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='key', full_name='Dianjing.protocol.TerritorySlot.key', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='report', full_name='Dianjing.protocol.TerritorySlot.report', index=6,
      number=8, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TERRITORYSLOT_REPORT, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=68,
  serialized_end=325,
)


_TERRITORYBUILDING = _descriptor.Descriptor(
  name='TerritoryBuilding',
  full_name='Dianjing.protocol.TerritoryBuilding',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.TerritoryBuilding.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='Dianjing.protocol.TerritoryBuilding.status', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='level', full_name='Dianjing.protocol.TerritoryBuilding.level', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='exp', full_name='Dianjing.protocol.TerritoryBuilding.exp', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='product_id', full_name='Dianjing.protocol.TerritoryBuilding.product_id', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='product_amount', full_name='Dianjing.protocol.TerritoryBuilding.product_amount', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='inspire_cost', full_name='Dianjing.protocol.TerritoryBuilding.inspire_cost', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='remained_inpire_times', full_name='Dianjing.protocol.TerritoryBuilding.remained_inpire_times', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='slots', full_name='Dianjing.protocol.TerritoryBuilding.slots', index=8,
      number=9, type=11, cpp_type=10, label=3,
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
  serialized_start=328,
  serialized_end=593,
)


_TERRITORYNOTIFY = _descriptor.Descriptor(
  name='TerritoryNotify',
  full_name='Dianjing.protocol.TerritoryNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TerritoryNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='act', full_name='Dianjing.protocol.TerritoryNotify.act', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='buildings', full_name='Dianjing.protocol.TerritoryNotify.buildings', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='training_hours', full_name='Dianjing.protocol.TerritoryNotify.training_hours', index=3,
      number=4, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='work_card', full_name='Dianjing.protocol.TerritoryNotify.work_card', index=4,
      number=5, type=5, cpp_type=1, label=2,
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
  serialized_start=596,
  serialized_end=770,
)


_TERRITORYTRAININGPREPAREREQUEST = _descriptor.Descriptor(
  name='TerritoryTrainingPrepareRequest',
  full_name='Dianjing.protocol.TerritoryTrainingPrepareRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TerritoryTrainingPrepareRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='building_id', full_name='Dianjing.protocol.TerritoryTrainingPrepareRequest.building_id', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='slot_id', full_name='Dianjing.protocol.TerritoryTrainingPrepareRequest.slot_id', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.TerritoryTrainingPrepareRequest.staff_id', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='hour', full_name='Dianjing.protocol.TerritoryTrainingPrepareRequest.hour', index=4,
      number=5, type=5, cpp_type=1, label=2,
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
  serialized_start=772,
  serialized_end=892,
)


_TERRITORYTRAININGPREPARERESPONSE = _descriptor.Descriptor(
  name='TerritoryTrainingPrepareResponse',
  full_name='Dianjing.protocol.TerritoryTrainingPrepareResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.TerritoryTrainingPrepareResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TerritoryTrainingPrepareResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='exp', full_name='Dianjing.protocol.TerritoryTrainingPrepareResponse.exp', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='product_id', full_name='Dianjing.protocol.TerritoryTrainingPrepareResponse.product_id', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='product_amount', full_name='Dianjing.protocol.TerritoryTrainingPrepareResponse.product_amount', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='key', full_name='Dianjing.protocol.TerritoryTrainingPrepareResponse.key', index=5,
      number=6, type=9, cpp_type=9, label=1,
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
  serialized_start=895,
  serialized_end=1029,
)


_TERRITORYTRAININGSTARTREQEUST = _descriptor.Descriptor(
  name='TerritoryTrainingStartReqeust',
  full_name='Dianjing.protocol.TerritoryTrainingStartReqeust',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TerritoryTrainingStartReqeust.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='key', full_name='Dianjing.protocol.TerritoryTrainingStartReqeust.key', index=1,
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
  serialized_start=1031,
  serialized_end=1092,
)


_TERRITORYTRAININGSTARTRESPONSE = _descriptor.Descriptor(
  name='TerritoryTrainingStartResponse',
  full_name='Dianjing.protocol.TerritoryTrainingStartResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.TerritoryTrainingStartResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TerritoryTrainingStartResponse.session', index=1,
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
  serialized_start=1094,
  serialized_end=1156,
)


_TERRITORYTRAININGGETREWARDREQEUST = _descriptor.Descriptor(
  name='TerritoryTrainingGetRewardReqeust',
  full_name='Dianjing.protocol.TerritoryTrainingGetRewardReqeust',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TerritoryTrainingGetRewardReqeust.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='key', full_name='Dianjing.protocol.TerritoryTrainingGetRewardReqeust.key', index=1,
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
  serialized_start=1158,
  serialized_end=1223,
)


_TERRITORYTRAININGGETREWARDRESPONSE = _descriptor.Descriptor(
  name='TerritoryTrainingGetRewardResponse',
  full_name='Dianjing.protocol.TerritoryTrainingGetRewardResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.TerritoryTrainingGetRewardResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.TerritoryTrainingGetRewardResponse.session', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='drop', full_name='Dianjing.protocol.TerritoryTrainingGetRewardResponse.drop', index=2,
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
  serialized_start=1225,
  serialized_end=1330,
)

_TERRITORYSLOT_REPORT.containing_type = _TERRITORYSLOT
_TERRITORYSLOT.fields_by_name['status'].enum_type = _TERRITORYSLOTSTATUS
_TERRITORYSLOT.fields_by_name['report'].message_type = _TERRITORYSLOT_REPORT
_TERRITORYBUILDING.fields_by_name['status'].enum_type = _TERRITORYBUILDINGSTATUS
_TERRITORYBUILDING.fields_by_name['slots'].message_type = _TERRITORYSLOT
_TERRITORYNOTIFY.fields_by_name['act'].enum_type = common__pb2._ACTION
_TERRITORYNOTIFY.fields_by_name['buildings'].message_type = _TERRITORYBUILDING
_TERRITORYTRAININGGETREWARDRESPONSE.fields_by_name['drop'].message_type = package__pb2._DROP
DESCRIPTOR.message_types_by_name['TerritorySlot'] = _TERRITORYSLOT
DESCRIPTOR.message_types_by_name['TerritoryBuilding'] = _TERRITORYBUILDING
DESCRIPTOR.message_types_by_name['TerritoryNotify'] = _TERRITORYNOTIFY
DESCRIPTOR.message_types_by_name['TerritoryTrainingPrepareRequest'] = _TERRITORYTRAININGPREPAREREQUEST
DESCRIPTOR.message_types_by_name['TerritoryTrainingPrepareResponse'] = _TERRITORYTRAININGPREPARERESPONSE
DESCRIPTOR.message_types_by_name['TerritoryTrainingStartReqeust'] = _TERRITORYTRAININGSTARTREQEUST
DESCRIPTOR.message_types_by_name['TerritoryTrainingStartResponse'] = _TERRITORYTRAININGSTARTRESPONSE
DESCRIPTOR.message_types_by_name['TerritoryTrainingGetRewardReqeust'] = _TERRITORYTRAININGGETREWARDREQEUST
DESCRIPTOR.message_types_by_name['TerritoryTrainingGetRewardResponse'] = _TERRITORYTRAININGGETREWARDRESPONSE
DESCRIPTOR.enum_types_by_name['TerritoryBuildingStatus'] = _TERRITORYBUILDINGSTATUS
DESCRIPTOR.enum_types_by_name['TerritorySlotStatus'] = _TERRITORYSLOTSTATUS

TerritorySlot = _reflection.GeneratedProtocolMessageType('TerritorySlot', (_message.Message,), dict(

  Report = _reflection.GeneratedProtocolMessageType('Report', (_message.Message,), dict(
    DESCRIPTOR = _TERRITORYSLOT_REPORT,
    __module__ = 'territory_pb2'
    # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritorySlot.Report)
    ))
  ,
  DESCRIPTOR = _TERRITORYSLOT,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritorySlot)
  ))
_sym_db.RegisterMessage(TerritorySlot)
_sym_db.RegisterMessage(TerritorySlot.Report)

TerritoryBuilding = _reflection.GeneratedProtocolMessageType('TerritoryBuilding', (_message.Message,), dict(
  DESCRIPTOR = _TERRITORYBUILDING,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritoryBuilding)
  ))
_sym_db.RegisterMessage(TerritoryBuilding)

TerritoryNotify = _reflection.GeneratedProtocolMessageType('TerritoryNotify', (_message.Message,), dict(
  DESCRIPTOR = _TERRITORYNOTIFY,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritoryNotify)
  ))
_sym_db.RegisterMessage(TerritoryNotify)

TerritoryTrainingPrepareRequest = _reflection.GeneratedProtocolMessageType('TerritoryTrainingPrepareRequest', (_message.Message,), dict(
  DESCRIPTOR = _TERRITORYTRAININGPREPAREREQUEST,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritoryTrainingPrepareRequest)
  ))
_sym_db.RegisterMessage(TerritoryTrainingPrepareRequest)

TerritoryTrainingPrepareResponse = _reflection.GeneratedProtocolMessageType('TerritoryTrainingPrepareResponse', (_message.Message,), dict(
  DESCRIPTOR = _TERRITORYTRAININGPREPARERESPONSE,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritoryTrainingPrepareResponse)
  ))
_sym_db.RegisterMessage(TerritoryTrainingPrepareResponse)

TerritoryTrainingStartReqeust = _reflection.GeneratedProtocolMessageType('TerritoryTrainingStartReqeust', (_message.Message,), dict(
  DESCRIPTOR = _TERRITORYTRAININGSTARTREQEUST,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritoryTrainingStartReqeust)
  ))
_sym_db.RegisterMessage(TerritoryTrainingStartReqeust)

TerritoryTrainingStartResponse = _reflection.GeneratedProtocolMessageType('TerritoryTrainingStartResponse', (_message.Message,), dict(
  DESCRIPTOR = _TERRITORYTRAININGSTARTRESPONSE,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritoryTrainingStartResponse)
  ))
_sym_db.RegisterMessage(TerritoryTrainingStartResponse)

TerritoryTrainingGetRewardReqeust = _reflection.GeneratedProtocolMessageType('TerritoryTrainingGetRewardReqeust', (_message.Message,), dict(
  DESCRIPTOR = _TERRITORYTRAININGGETREWARDREQEUST,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritoryTrainingGetRewardReqeust)
  ))
_sym_db.RegisterMessage(TerritoryTrainingGetRewardReqeust)

TerritoryTrainingGetRewardResponse = _reflection.GeneratedProtocolMessageType('TerritoryTrainingGetRewardResponse', (_message.Message,), dict(
  DESCRIPTOR = _TERRITORYTRAININGGETREWARDRESPONSE,
  __module__ = 'territory_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.TerritoryTrainingGetRewardResponse)
  ))
_sym_db.RegisterMessage(TerritoryTrainingGetRewardResponse)


# @@protoc_insertion_point(module_scope)
