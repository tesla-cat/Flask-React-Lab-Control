# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: qm/pb/general_messages.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='qm/pb/general_messages.proto',
  package='qm.grpc.general_messages',
  syntax='proto3',
  serialized_options=_b('\n\027qm.grpc.generalMessagesB\024GeneralMessagesProtoP\001\242\002\003HLW'),
  serialized_pb=_b('\n\x1cqm/pb/general_messages.proto\x12\x18qm.grpc.general_messages\"-\n\x0c\x45rrorMessage\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t*Z\n\x0cMessageLevel\x12\x17\n\x13Message_LEVEL_ERROR\x10\x00\x12\x19\n\x15Message_LEVEL_WARNING\x10\x01\x12\x16\n\x12Message_LEVEL_INFO\x10\x02\x42\x37\n\x17qm.grpc.generalMessagesB\x14GeneralMessagesProtoP\x01\xa2\x02\x03HLWb\x06proto3')
)

_MESSAGELEVEL = _descriptor.EnumDescriptor(
  name='MessageLevel',
  full_name='qm.grpc.general_messages.MessageLevel',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='Message_LEVEL_ERROR', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='Message_LEVEL_WARNING', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='Message_LEVEL_INFO', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=105,
  serialized_end=195,
)
_sym_db.RegisterEnumDescriptor(_MESSAGELEVEL)

MessageLevel = enum_type_wrapper.EnumTypeWrapper(_MESSAGELEVEL)
Message_LEVEL_ERROR = 0
Message_LEVEL_WARNING = 1
Message_LEVEL_INFO = 2



_ERRORMESSAGE = _descriptor.Descriptor(
  name='ErrorMessage',
  full_name='qm.grpc.general_messages.ErrorMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='qm.grpc.general_messages.ErrorMessage.code', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message', full_name='qm.grpc.general_messages.ErrorMessage.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=58,
  serialized_end=103,
)

DESCRIPTOR.message_types_by_name['ErrorMessage'] = _ERRORMESSAGE
DESCRIPTOR.enum_types_by_name['MessageLevel'] = _MESSAGELEVEL
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ErrorMessage = _reflection.GeneratedProtocolMessageType('ErrorMessage', (_message.Message,), {
  'DESCRIPTOR' : _ERRORMESSAGE,
  '__module__' : 'qm.pb.general_messages_pb2'
  # @@protoc_insertion_point(class_scope:qm.grpc.general_messages.ErrorMessage)
  })
_sym_db.RegisterMessage(ErrorMessage)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
