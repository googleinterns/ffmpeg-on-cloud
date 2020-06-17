# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ffmpeg_worker.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='ffmpeg_worker.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x13\x66\x66mpeg_worker.proto\"\x13\n\x03Log\x12\x0c\n\x04text\x18\x01 \x01(\t\":\n\x07Request\x12\x16\n\x0einput_filename\x18\x01 \x01(\t\x12\x17\n\x0foutput_filename\x18\x02 \x01(\t2)\n\x06\x46\x46mpeg\x12\x1f\n\ttranscode\x12\x08.Request\x1a\x04.Log\"\x00\x30\x01\x62\x06proto3'
)




_LOG = _descriptor.Descriptor(
  name='Log',
  full_name='Log',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='text', full_name='Log.text', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=23,
  serialized_end=42,
)


_REQUEST = _descriptor.Descriptor(
  name='Request',
  full_name='Request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='input_filename', full_name='Request.input_filename', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='output_filename', full_name='Request.output_filename', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=44,
  serialized_end=102,
)

DESCRIPTOR.message_types_by_name['Log'] = _LOG
DESCRIPTOR.message_types_by_name['Request'] = _REQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Log = _reflection.GeneratedProtocolMessageType('Log', (_message.Message,), {
  'DESCRIPTOR' : _LOG,
  '__module__' : 'ffmpeg_worker_pb2'
  # @@protoc_insertion_point(class_scope:Log)
  })
_sym_db.RegisterMessage(Log)

Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), {
  'DESCRIPTOR' : _REQUEST,
  '__module__' : 'ffmpeg_worker_pb2'
  # @@protoc_insertion_point(class_scope:Request)
  })
_sym_db.RegisterMessage(Request)



_FFMPEG = _descriptor.ServiceDescriptor(
  name='FFmpeg',
  full_name='FFmpeg',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=104,
  serialized_end=145,
  methods=[
  _descriptor.MethodDescriptor(
    name='transcode',
    full_name='FFmpeg.transcode',
    index=0,
    containing_service=None,
    input_type=_REQUEST,
    output_type=_LOG,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_FFMPEG)

DESCRIPTOR.services_by_name['FFmpeg'] = _FFMPEG

# @@protoc_insertion_point(module_scope)
