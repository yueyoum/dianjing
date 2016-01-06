# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: skill.proto

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
  name='skill.proto',
  package='Dianjing.protocol',
  syntax='proto2',
  serialized_pb=_b('\n\x0bskill.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\"J\n\x05Skill\x12\n\n\x02id\x18\x01 \x02(\x05\x12\r\n\x05level\x18\x02 \x02(\x05\x12\x0e\n\x06locked\x18\x03 \x02(\x08\x12\x16\n\x0eupgrade_end_at\x18\x04 \x02(\x03\"\xd1\x01\n\x0bSkillNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12&\n\x03\x61\x63t\x18\x02 \x02(\x0e\x32\x19.Dianjing.protocol.Action\x12?\n\x0cstaff_skills\x18\x03 \x03(\x0b\x32).Dianjing.protocol.SkillNotify.StaffSkill\x1aH\n\nStaffSkill\x12\x10\n\x08staff_id\x18\x01 \x02(\x05\x12(\n\x06skills\x18\x02 \x03(\x0b\x32\x18.Dianjing.protocol.Skill\"M\n\x16SkillLockToggleRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x10\n\x08staff_id\x18\x02 \x02(\x05\x12\x10\n\x08skill_id\x18\x03 \x02(\x05\"7\n\x17SkillLockToggleResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"5\n\x10SkillWashRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x10\n\x08staff_id\x18\x02 \x02(\x05\"1\n\x11SkillWashResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"J\n\x13SkillUpgradeRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x10\n\x08staff_id\x18\x02 \x02(\x05\x12\x10\n\x08skill_id\x18\x03 \x02(\x05\"4\n\x14SkillUpgradeResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"Q\n\x1aSkillUpgradeSpeedupRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x10\n\x08staff_id\x18\x02 \x02(\x05\x12\x10\n\x08skill_id\x18\x03 \x02(\x05\";\n\x1bSkillUpgradeSpeedupResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c')
  ,
  dependencies=[common__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_SKILL = _descriptor.Descriptor(
  name='Skill',
  full_name='Dianjing.protocol.Skill',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Dianjing.protocol.Skill.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='level', full_name='Dianjing.protocol.Skill.level', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='locked', full_name='Dianjing.protocol.Skill.locked', index=2,
      number=3, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='upgrade_end_at', full_name='Dianjing.protocol.Skill.upgrade_end_at', index=3,
      number=4, type=3, cpp_type=2, label=2,
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
  serialized_start=48,
  serialized_end=122,
)


_SKILLNOTIFY_STAFFSKILL = _descriptor.Descriptor(
  name='StaffSkill',
  full_name='Dianjing.protocol.SkillNotify.StaffSkill',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.SkillNotify.StaffSkill.staff_id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='skills', full_name='Dianjing.protocol.SkillNotify.StaffSkill.skills', index=1,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=262,
  serialized_end=334,
)

_SKILLNOTIFY = _descriptor.Descriptor(
  name='SkillNotify',
  full_name='Dianjing.protocol.SkillNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='act', full_name='Dianjing.protocol.SkillNotify.act', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_skills', full_name='Dianjing.protocol.SkillNotify.staff_skills', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_SKILLNOTIFY_STAFFSKILL, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=125,
  serialized_end=334,
)


_SKILLLOCKTOGGLEREQUEST = _descriptor.Descriptor(
  name='SkillLockToggleRequest',
  full_name='Dianjing.protocol.SkillLockToggleRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillLockToggleRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.SkillLockToggleRequest.staff_id', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='skill_id', full_name='Dianjing.protocol.SkillLockToggleRequest.skill_id', index=2,
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
  serialized_start=336,
  serialized_end=413,
)


_SKILLLOCKTOGGLERESPONSE = _descriptor.Descriptor(
  name='SkillLockToggleResponse',
  full_name='Dianjing.protocol.SkillLockToggleResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.SkillLockToggleResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillLockToggleResponse.session', index=1,
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
  serialized_start=415,
  serialized_end=470,
)


_SKILLWASHREQUEST = _descriptor.Descriptor(
  name='SkillWashRequest',
  full_name='Dianjing.protocol.SkillWashRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillWashRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.SkillWashRequest.staff_id', index=1,
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
  serialized_start=472,
  serialized_end=525,
)


_SKILLWASHRESPONSE = _descriptor.Descriptor(
  name='SkillWashResponse',
  full_name='Dianjing.protocol.SkillWashResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.SkillWashResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillWashResponse.session', index=1,
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
  serialized_start=527,
  serialized_end=576,
)


_SKILLUPGRADEREQUEST = _descriptor.Descriptor(
  name='SkillUpgradeRequest',
  full_name='Dianjing.protocol.SkillUpgradeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillUpgradeRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.SkillUpgradeRequest.staff_id', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='skill_id', full_name='Dianjing.protocol.SkillUpgradeRequest.skill_id', index=2,
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
  serialized_start=578,
  serialized_end=652,
)


_SKILLUPGRADERESPONSE = _descriptor.Descriptor(
  name='SkillUpgradeResponse',
  full_name='Dianjing.protocol.SkillUpgradeResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.SkillUpgradeResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillUpgradeResponse.session', index=1,
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
  serialized_start=654,
  serialized_end=706,
)


_SKILLUPGRADESPEEDUPREQUEST = _descriptor.Descriptor(
  name='SkillUpgradeSpeedupRequest',
  full_name='Dianjing.protocol.SkillUpgradeSpeedupRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillUpgradeSpeedupRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.SkillUpgradeSpeedupRequest.staff_id', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='skill_id', full_name='Dianjing.protocol.SkillUpgradeSpeedupRequest.skill_id', index=2,
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
  serialized_start=708,
  serialized_end=789,
)


_SKILLUPGRADESPEEDUPRESPONSE = _descriptor.Descriptor(
  name='SkillUpgradeSpeedupResponse',
  full_name='Dianjing.protocol.SkillUpgradeSpeedupResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.SkillUpgradeSpeedupResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.SkillUpgradeSpeedupResponse.session', index=1,
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
  serialized_start=791,
  serialized_end=850,
)

_SKILLNOTIFY_STAFFSKILL.fields_by_name['skills'].message_type = _SKILL
_SKILLNOTIFY_STAFFSKILL.containing_type = _SKILLNOTIFY
_SKILLNOTIFY.fields_by_name['act'].enum_type = common__pb2._ACTION
_SKILLNOTIFY.fields_by_name['staff_skills'].message_type = _SKILLNOTIFY_STAFFSKILL
DESCRIPTOR.message_types_by_name['Skill'] = _SKILL
DESCRIPTOR.message_types_by_name['SkillNotify'] = _SKILLNOTIFY
DESCRIPTOR.message_types_by_name['SkillLockToggleRequest'] = _SKILLLOCKTOGGLEREQUEST
DESCRIPTOR.message_types_by_name['SkillLockToggleResponse'] = _SKILLLOCKTOGGLERESPONSE
DESCRIPTOR.message_types_by_name['SkillWashRequest'] = _SKILLWASHREQUEST
DESCRIPTOR.message_types_by_name['SkillWashResponse'] = _SKILLWASHRESPONSE
DESCRIPTOR.message_types_by_name['SkillUpgradeRequest'] = _SKILLUPGRADEREQUEST
DESCRIPTOR.message_types_by_name['SkillUpgradeResponse'] = _SKILLUPGRADERESPONSE
DESCRIPTOR.message_types_by_name['SkillUpgradeSpeedupRequest'] = _SKILLUPGRADESPEEDUPREQUEST
DESCRIPTOR.message_types_by_name['SkillUpgradeSpeedupResponse'] = _SKILLUPGRADESPEEDUPRESPONSE

Skill = _reflection.GeneratedProtocolMessageType('Skill', (_message.Message,), dict(
  DESCRIPTOR = _SKILL,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.Skill)
  ))
_sym_db.RegisterMessage(Skill)

SkillNotify = _reflection.GeneratedProtocolMessageType('SkillNotify', (_message.Message,), dict(

  StaffSkill = _reflection.GeneratedProtocolMessageType('StaffSkill', (_message.Message,), dict(
    DESCRIPTOR = _SKILLNOTIFY_STAFFSKILL,
    __module__ = 'skill_pb2'
    # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillNotify.StaffSkill)
    ))
  ,
  DESCRIPTOR = _SKILLNOTIFY,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillNotify)
  ))
_sym_db.RegisterMessage(SkillNotify)
_sym_db.RegisterMessage(SkillNotify.StaffSkill)

SkillLockToggleRequest = _reflection.GeneratedProtocolMessageType('SkillLockToggleRequest', (_message.Message,), dict(
  DESCRIPTOR = _SKILLLOCKTOGGLEREQUEST,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillLockToggleRequest)
  ))
_sym_db.RegisterMessage(SkillLockToggleRequest)

SkillLockToggleResponse = _reflection.GeneratedProtocolMessageType('SkillLockToggleResponse', (_message.Message,), dict(
  DESCRIPTOR = _SKILLLOCKTOGGLERESPONSE,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillLockToggleResponse)
  ))
_sym_db.RegisterMessage(SkillLockToggleResponse)

SkillWashRequest = _reflection.GeneratedProtocolMessageType('SkillWashRequest', (_message.Message,), dict(
  DESCRIPTOR = _SKILLWASHREQUEST,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillWashRequest)
  ))
_sym_db.RegisterMessage(SkillWashRequest)

SkillWashResponse = _reflection.GeneratedProtocolMessageType('SkillWashResponse', (_message.Message,), dict(
  DESCRIPTOR = _SKILLWASHRESPONSE,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillWashResponse)
  ))
_sym_db.RegisterMessage(SkillWashResponse)

SkillUpgradeRequest = _reflection.GeneratedProtocolMessageType('SkillUpgradeRequest', (_message.Message,), dict(
  DESCRIPTOR = _SKILLUPGRADEREQUEST,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillUpgradeRequest)
  ))
_sym_db.RegisterMessage(SkillUpgradeRequest)

SkillUpgradeResponse = _reflection.GeneratedProtocolMessageType('SkillUpgradeResponse', (_message.Message,), dict(
  DESCRIPTOR = _SKILLUPGRADERESPONSE,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillUpgradeResponse)
  ))
_sym_db.RegisterMessage(SkillUpgradeResponse)

SkillUpgradeSpeedupRequest = _reflection.GeneratedProtocolMessageType('SkillUpgradeSpeedupRequest', (_message.Message,), dict(
  DESCRIPTOR = _SKILLUPGRADESPEEDUPREQUEST,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillUpgradeSpeedupRequest)
  ))
_sym_db.RegisterMessage(SkillUpgradeSpeedupRequest)

SkillUpgradeSpeedupResponse = _reflection.GeneratedProtocolMessageType('SkillUpgradeSpeedupResponse', (_message.Message,), dict(
  DESCRIPTOR = _SKILLUPGRADESPEEDUPRESPONSE,
  __module__ = 'skill_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SkillUpgradeSpeedupResponse)
  ))
_sym_db.RegisterMessage(SkillUpgradeSpeedupResponse)


# @@protoc_insertion_point(module_scope)
