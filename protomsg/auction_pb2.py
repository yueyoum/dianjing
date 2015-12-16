# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: auction.proto

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
import staff_pb2 as staff__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='auction.proto',
  package='Dianjing.protocol',
  syntax='proto2',
  serialized_pb=_b('\n\rauction.proto\x12\x11\x44ianjing.protocol\x1a\x0c\x63ommon.proto\x1a\x0bstaff.proto\"\x9e\x01\n\x0b\x41uctionItem\x12\x0f\n\x07item_id\x18\x01 \x02(\t\x12\x11\n\tclub_name\x18\x02 \x02(\t\x12\x10\n\x08staff_id\x18\x03 \x02(\x05\x12\x12\n\nstart_time\x18\x05 \x02(\x03\x12\x0e\n\x06\x65nd_at\x18\x06 \x02(\x03\x12\x11\n\tmin_price\x18\x07 \x02(\x05\x12\x11\n\tmax_price\x18\x08 \x02(\x05\x12\x0f\n\x07\x62idding\x18\t \x02(\x05\",\n\x0fSearchCondition\x12\n\n\x02tp\x18\x01 \x02(\x05\x12\r\n\x05value\x18\x02 \x02(\x05\"\x80\x01\n\x16StaffAuctionUserNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12&\n\x03\x61\x63t\x18\x02 \x02(\x0e\x32\x19.Dianjing.protocol.Action\x12-\n\x05items\x18\x03 \x03(\x0b\x32\x1e.Dianjing.protocol.AuctionItem\"|\n\x12StaffAuctionNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12&\n\x03\x61\x63t\x18\x02 \x02(\x0e\x32\x19.Dianjing.protocol.Action\x12-\n\x05items\x18\x03 \x03(\x0b\x32\x1e.Dianjing.protocol.AuctionItem\"c\n\x19StaffAuctionSearchRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x35\n\tcondition\x18\x02 \x03(\x0b\x32\".Dianjing.protocol.SearchCondition\":\n\x1aStaffAuctionSearchResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"n\n\x17StaffAuctionSellRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x10\n\x08staff_id\x18\x02 \x02(\x05\x12\n\n\x02tp\x18\x03 \x02(\x05\x12\x11\n\tmin_price\x18\x04 \x02(\x05\x12\x11\n\tmax_price\x18\x05 \x02(\x05\"8\n\x18StaffAuctionSellResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"=\n\x19StaffAuctionCancelRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0f\n\x07item_id\x18\x02 \x02(\t\":\n\x1aStaffAuctionCancelResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"L\n\x19StaffAuctionBidingRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0f\n\x07item_id\x18\x02 \x02(\t\x12\r\n\x05price\x18\x03 \x02(\x05\";\n\x1bStaffAuctionBiddingResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"D\n StaffAuctionUserItemRemoveNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x0f\n\x07item_id\x18\x02 \x02(\t\"*\n\x17StaffAuctionListRequest\x12\x0f\n\x07session\x18\x01 \x02(\x0c\"8\n\x18StaffAuctionListResponse\x12\x0b\n\x03ret\x18\x01 \x02(\x05\x12\x0f\n\x07session\x18\x02 \x02(\x0c\"Q\n\x10\x41uctionStaffItem\x12-\n\x05items\x18\x01 \x02(\x0b\x32\x1e.Dianjing.protocol.AuctionItem\x12\x0e\n\x06my_bid\x18\x02 \x02(\x05\"a\n\x16StaffAuctionListNotify\x12\x0f\n\x07session\x18\x01 \x02(\x0c\x12\x36\n\titem_info\x18\x02 \x03(\x0b\x32#.Dianjing.protocol.AuctionStaffItem*=\n\x12\x41uctionItemTaxType\x12\x0b\n\x07hours_8\x10\x01\x12\x0c\n\x08hours_16\x10\x02\x12\x0c\n\x08hours_24\x10\x03')
  ,
  dependencies=[common__pb2.DESCRIPTOR,staff__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_AUCTIONITEMTAXTYPE = _descriptor.EnumDescriptor(
  name='AuctionItemTaxType',
  full_name='Dianjing.protocol.AuctionItemTaxType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='hours_8', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='hours_16', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='hours_24', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1474,
  serialized_end=1535,
)
_sym_db.RegisterEnumDescriptor(_AUCTIONITEMTAXTYPE)

AuctionItemTaxType = enum_type_wrapper.EnumTypeWrapper(_AUCTIONITEMTAXTYPE)
hours_8 = 1
hours_16 = 2
hours_24 = 3



_AUCTIONITEM = _descriptor.Descriptor(
  name='AuctionItem',
  full_name='Dianjing.protocol.AuctionItem',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='item_id', full_name='Dianjing.protocol.AuctionItem.item_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='club_name', full_name='Dianjing.protocol.AuctionItem.club_name', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.AuctionItem.staff_id', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='start_time', full_name='Dianjing.protocol.AuctionItem.start_time', index=3,
      number=5, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='end_at', full_name='Dianjing.protocol.AuctionItem.end_at', index=4,
      number=6, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='min_price', full_name='Dianjing.protocol.AuctionItem.min_price', index=5,
      number=7, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_price', full_name='Dianjing.protocol.AuctionItem.max_price', index=6,
      number=8, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bidding', full_name='Dianjing.protocol.AuctionItem.bidding', index=7,
      number=9, type=5, cpp_type=1, label=2,
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
  serialized_start=64,
  serialized_end=222,
)


_SEARCHCONDITION = _descriptor.Descriptor(
  name='SearchCondition',
  full_name='Dianjing.protocol.SearchCondition',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tp', full_name='Dianjing.protocol.SearchCondition.tp', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='Dianjing.protocol.SearchCondition.value', index=1,
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
  serialized_start=224,
  serialized_end=268,
)


_STAFFAUCTIONUSERNOTIFY = _descriptor.Descriptor(
  name='StaffAuctionUserNotify',
  full_name='Dianjing.protocol.StaffAuctionUserNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionUserNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='act', full_name='Dianjing.protocol.StaffAuctionUserNotify.act', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='items', full_name='Dianjing.protocol.StaffAuctionUserNotify.items', index=2,
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
  serialized_start=271,
  serialized_end=399,
)


_STAFFAUCTIONNOTIFY = _descriptor.Descriptor(
  name='StaffAuctionNotify',
  full_name='Dianjing.protocol.StaffAuctionNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='act', full_name='Dianjing.protocol.StaffAuctionNotify.act', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='items', full_name='Dianjing.protocol.StaffAuctionNotify.items', index=2,
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
  serialized_start=401,
  serialized_end=525,
)


_STAFFAUCTIONSEARCHREQUEST = _descriptor.Descriptor(
  name='StaffAuctionSearchRequest',
  full_name='Dianjing.protocol.StaffAuctionSearchRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionSearchRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='condition', full_name='Dianjing.protocol.StaffAuctionSearchRequest.condition', index=1,
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
  serialized_start=527,
  serialized_end=626,
)


_STAFFAUCTIONSEARCHRESPONSE = _descriptor.Descriptor(
  name='StaffAuctionSearchResponse',
  full_name='Dianjing.protocol.StaffAuctionSearchResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.StaffAuctionSearchResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionSearchResponse.session', index=1,
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
  serialized_start=628,
  serialized_end=686,
)


_STAFFAUCTIONSELLREQUEST = _descriptor.Descriptor(
  name='StaffAuctionSellRequest',
  full_name='Dianjing.protocol.StaffAuctionSellRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionSellRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='staff_id', full_name='Dianjing.protocol.StaffAuctionSellRequest.staff_id', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tp', full_name='Dianjing.protocol.StaffAuctionSellRequest.tp', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='min_price', full_name='Dianjing.protocol.StaffAuctionSellRequest.min_price', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_price', full_name='Dianjing.protocol.StaffAuctionSellRequest.max_price', index=4,
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
  serialized_start=688,
  serialized_end=798,
)


_STAFFAUCTIONSELLRESPONSE = _descriptor.Descriptor(
  name='StaffAuctionSellResponse',
  full_name='Dianjing.protocol.StaffAuctionSellResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.StaffAuctionSellResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionSellResponse.session', index=1,
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
  serialized_start=800,
  serialized_end=856,
)


_STAFFAUCTIONCANCELREQUEST = _descriptor.Descriptor(
  name='StaffAuctionCancelRequest',
  full_name='Dianjing.protocol.StaffAuctionCancelRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionCancelRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='item_id', full_name='Dianjing.protocol.StaffAuctionCancelRequest.item_id', index=1,
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
  serialized_start=858,
  serialized_end=919,
)


_STAFFAUCTIONCANCELRESPONSE = _descriptor.Descriptor(
  name='StaffAuctionCancelResponse',
  full_name='Dianjing.protocol.StaffAuctionCancelResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.StaffAuctionCancelResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionCancelResponse.session', index=1,
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
  serialized_start=921,
  serialized_end=979,
)


_STAFFAUCTIONBIDINGREQUEST = _descriptor.Descriptor(
  name='StaffAuctionBidingRequest',
  full_name='Dianjing.protocol.StaffAuctionBidingRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionBidingRequest.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='item_id', full_name='Dianjing.protocol.StaffAuctionBidingRequest.item_id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='price', full_name='Dianjing.protocol.StaffAuctionBidingRequest.price', index=2,
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
  serialized_start=981,
  serialized_end=1057,
)


_STAFFAUCTIONBIDDINGRESPONSE = _descriptor.Descriptor(
  name='StaffAuctionBiddingResponse',
  full_name='Dianjing.protocol.StaffAuctionBiddingResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.StaffAuctionBiddingResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionBiddingResponse.session', index=1,
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
  serialized_start=1059,
  serialized_end=1118,
)


_STAFFAUCTIONUSERITEMREMOVENOTIFY = _descriptor.Descriptor(
  name='StaffAuctionUserItemRemoveNotify',
  full_name='Dianjing.protocol.StaffAuctionUserItemRemoveNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionUserItemRemoveNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='item_id', full_name='Dianjing.protocol.StaffAuctionUserItemRemoveNotify.item_id', index=1,
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
  serialized_start=1120,
  serialized_end=1188,
)


_STAFFAUCTIONLISTREQUEST = _descriptor.Descriptor(
  name='StaffAuctionListRequest',
  full_name='Dianjing.protocol.StaffAuctionListRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionListRequest.session', index=0,
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
  serialized_start=1190,
  serialized_end=1232,
)


_STAFFAUCTIONLISTRESPONSE = _descriptor.Descriptor(
  name='StaffAuctionListResponse',
  full_name='Dianjing.protocol.StaffAuctionListResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret', full_name='Dianjing.protocol.StaffAuctionListResponse.ret', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionListResponse.session', index=1,
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
  serialized_start=1234,
  serialized_end=1290,
)


_AUCTIONSTAFFITEM = _descriptor.Descriptor(
  name='AuctionStaffItem',
  full_name='Dianjing.protocol.AuctionStaffItem',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='items', full_name='Dianjing.protocol.AuctionStaffItem.items', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='my_bid', full_name='Dianjing.protocol.AuctionStaffItem.my_bid', index=1,
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
  serialized_start=1292,
  serialized_end=1373,
)


_STAFFAUCTIONLISTNOTIFY = _descriptor.Descriptor(
  name='StaffAuctionListNotify',
  full_name='Dianjing.protocol.StaffAuctionListNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session', full_name='Dianjing.protocol.StaffAuctionListNotify.session', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='item_info', full_name='Dianjing.protocol.StaffAuctionListNotify.item_info', index=1,
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
  serialized_start=1375,
  serialized_end=1472,
)

_STAFFAUCTIONUSERNOTIFY.fields_by_name['act'].enum_type = common__pb2._ACTION
_STAFFAUCTIONUSERNOTIFY.fields_by_name['items'].message_type = _AUCTIONITEM
_STAFFAUCTIONNOTIFY.fields_by_name['act'].enum_type = common__pb2._ACTION
_STAFFAUCTIONNOTIFY.fields_by_name['items'].message_type = _AUCTIONITEM
_STAFFAUCTIONSEARCHREQUEST.fields_by_name['condition'].message_type = _SEARCHCONDITION
_AUCTIONSTAFFITEM.fields_by_name['items'].message_type = _AUCTIONITEM
_STAFFAUCTIONLISTNOTIFY.fields_by_name['item_info'].message_type = _AUCTIONSTAFFITEM
DESCRIPTOR.message_types_by_name['AuctionItem'] = _AUCTIONITEM
DESCRIPTOR.message_types_by_name['SearchCondition'] = _SEARCHCONDITION
DESCRIPTOR.message_types_by_name['StaffAuctionUserNotify'] = _STAFFAUCTIONUSERNOTIFY
DESCRIPTOR.message_types_by_name['StaffAuctionNotify'] = _STAFFAUCTIONNOTIFY
DESCRIPTOR.message_types_by_name['StaffAuctionSearchRequest'] = _STAFFAUCTIONSEARCHREQUEST
DESCRIPTOR.message_types_by_name['StaffAuctionSearchResponse'] = _STAFFAUCTIONSEARCHRESPONSE
DESCRIPTOR.message_types_by_name['StaffAuctionSellRequest'] = _STAFFAUCTIONSELLREQUEST
DESCRIPTOR.message_types_by_name['StaffAuctionSellResponse'] = _STAFFAUCTIONSELLRESPONSE
DESCRIPTOR.message_types_by_name['StaffAuctionCancelRequest'] = _STAFFAUCTIONCANCELREQUEST
DESCRIPTOR.message_types_by_name['StaffAuctionCancelResponse'] = _STAFFAUCTIONCANCELRESPONSE
DESCRIPTOR.message_types_by_name['StaffAuctionBidingRequest'] = _STAFFAUCTIONBIDINGREQUEST
DESCRIPTOR.message_types_by_name['StaffAuctionBiddingResponse'] = _STAFFAUCTIONBIDDINGRESPONSE
DESCRIPTOR.message_types_by_name['StaffAuctionUserItemRemoveNotify'] = _STAFFAUCTIONUSERITEMREMOVENOTIFY
DESCRIPTOR.message_types_by_name['StaffAuctionListRequest'] = _STAFFAUCTIONLISTREQUEST
DESCRIPTOR.message_types_by_name['StaffAuctionListResponse'] = _STAFFAUCTIONLISTRESPONSE
DESCRIPTOR.message_types_by_name['AuctionStaffItem'] = _AUCTIONSTAFFITEM
DESCRIPTOR.message_types_by_name['StaffAuctionListNotify'] = _STAFFAUCTIONLISTNOTIFY
DESCRIPTOR.enum_types_by_name['AuctionItemTaxType'] = _AUCTIONITEMTAXTYPE

AuctionItem = _reflection.GeneratedProtocolMessageType('AuctionItem', (_message.Message,), dict(
  DESCRIPTOR = _AUCTIONITEM,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.AuctionItem)
  ))
_sym_db.RegisterMessage(AuctionItem)

SearchCondition = _reflection.GeneratedProtocolMessageType('SearchCondition', (_message.Message,), dict(
  DESCRIPTOR = _SEARCHCONDITION,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.SearchCondition)
  ))
_sym_db.RegisterMessage(SearchCondition)

StaffAuctionUserNotify = _reflection.GeneratedProtocolMessageType('StaffAuctionUserNotify', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONUSERNOTIFY,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionUserNotify)
  ))
_sym_db.RegisterMessage(StaffAuctionUserNotify)

StaffAuctionNotify = _reflection.GeneratedProtocolMessageType('StaffAuctionNotify', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONNOTIFY,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionNotify)
  ))
_sym_db.RegisterMessage(StaffAuctionNotify)

StaffAuctionSearchRequest = _reflection.GeneratedProtocolMessageType('StaffAuctionSearchRequest', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONSEARCHREQUEST,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionSearchRequest)
  ))
_sym_db.RegisterMessage(StaffAuctionSearchRequest)

StaffAuctionSearchResponse = _reflection.GeneratedProtocolMessageType('StaffAuctionSearchResponse', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONSEARCHRESPONSE,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionSearchResponse)
  ))
_sym_db.RegisterMessage(StaffAuctionSearchResponse)

StaffAuctionSellRequest = _reflection.GeneratedProtocolMessageType('StaffAuctionSellRequest', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONSELLREQUEST,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionSellRequest)
  ))
_sym_db.RegisterMessage(StaffAuctionSellRequest)

StaffAuctionSellResponse = _reflection.GeneratedProtocolMessageType('StaffAuctionSellResponse', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONSELLRESPONSE,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionSellResponse)
  ))
_sym_db.RegisterMessage(StaffAuctionSellResponse)

StaffAuctionCancelRequest = _reflection.GeneratedProtocolMessageType('StaffAuctionCancelRequest', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONCANCELREQUEST,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionCancelRequest)
  ))
_sym_db.RegisterMessage(StaffAuctionCancelRequest)

StaffAuctionCancelResponse = _reflection.GeneratedProtocolMessageType('StaffAuctionCancelResponse', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONCANCELRESPONSE,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionCancelResponse)
  ))
_sym_db.RegisterMessage(StaffAuctionCancelResponse)

StaffAuctionBidingRequest = _reflection.GeneratedProtocolMessageType('StaffAuctionBidingRequest', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONBIDINGREQUEST,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionBidingRequest)
  ))
_sym_db.RegisterMessage(StaffAuctionBidingRequest)

StaffAuctionBiddingResponse = _reflection.GeneratedProtocolMessageType('StaffAuctionBiddingResponse', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONBIDDINGRESPONSE,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionBiddingResponse)
  ))
_sym_db.RegisterMessage(StaffAuctionBiddingResponse)

StaffAuctionUserItemRemoveNotify = _reflection.GeneratedProtocolMessageType('StaffAuctionUserItemRemoveNotify', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONUSERITEMREMOVENOTIFY,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionUserItemRemoveNotify)
  ))
_sym_db.RegisterMessage(StaffAuctionUserItemRemoveNotify)

StaffAuctionListRequest = _reflection.GeneratedProtocolMessageType('StaffAuctionListRequest', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONLISTREQUEST,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionListRequest)
  ))
_sym_db.RegisterMessage(StaffAuctionListRequest)

StaffAuctionListResponse = _reflection.GeneratedProtocolMessageType('StaffAuctionListResponse', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONLISTRESPONSE,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionListResponse)
  ))
_sym_db.RegisterMessage(StaffAuctionListResponse)

AuctionStaffItem = _reflection.GeneratedProtocolMessageType('AuctionStaffItem', (_message.Message,), dict(
  DESCRIPTOR = _AUCTIONSTAFFITEM,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.AuctionStaffItem)
  ))
_sym_db.RegisterMessage(AuctionStaffItem)

StaffAuctionListNotify = _reflection.GeneratedProtocolMessageType('StaffAuctionListNotify', (_message.Message,), dict(
  DESCRIPTOR = _STAFFAUCTIONLISTNOTIFY,
  __module__ = 'auction_pb2'
  # @@protoc_insertion_point(class_scope:Dianjing.protocol.StaffAuctionListNotify)
  ))
_sym_db.RegisterMessage(StaffAuctionListNotify)


# @@protoc_insertion_point(module_scope)
