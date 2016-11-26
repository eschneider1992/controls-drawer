"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""

try:
    import cStringIO.StringIO as BytesIO
except ImportError:
    from io import BytesIO
import struct

import lcmtypes.image_request_t

class image_t(object):
    __slots__ = ["utime", "action_id", "request", "width", "height", "row_stride", "FPS", "brightness", "contrast", "num_data", "data"]

    def __init__(self):
        self.utime = 0
        self.action_id = 0
        self.request = lcmtypes.image_request_t()
        self.width = 0
        self.height = 0
        self.row_stride = 0
        self.FPS = 0
        self.brightness = 0.0
        self.contrast = 0.0
        self.num_data = 0
        self.data = []

    def encode(self):
        buf = BytesIO()
        buf.write(image_t._get_packed_fingerprint())
        self._encode_one(buf)
        return buf.getvalue()

    def _encode_one(self, buf):
        buf.write(struct.pack(">qq", self.utime, self.action_id))
        assert self.request._get_packed_fingerprint() == lcmtypes.image_request_t._get_packed_fingerprint()
        self.request._encode_one(buf)
        buf.write(struct.pack(">hhhhffi", self.width, self.height, self.row_stride, self.FPS, self.brightness, self.contrast, self.num_data))
        buf.write(struct.pack('>%dh' % self.num_data, *self.data[:self.num_data]))

    def decode(data):
        if hasattr(data, 'read'):
            buf = data
        else:
            buf = BytesIO(data)
        if buf.read(8) != image_t._get_packed_fingerprint():
            raise ValueError("Decode error")
        return image_t._decode_one(buf)
    decode = staticmethod(decode)

    def _decode_one(buf):
        self = image_t()
        self.utime, self.action_id = struct.unpack(">qq", buf.read(16))
        self.request = lcmtypes.image_request_t._decode_one(buf)
        self.width, self.height, self.row_stride, self.FPS, self.brightness, self.contrast, self.num_data = struct.unpack(">hhhhffi", buf.read(20))
        self.data = struct.unpack('>%dh' % self.num_data, buf.read(self.num_data * 2))
        return self
    _decode_one = staticmethod(_decode_one)

    _hash = None
    def _get_hash_recursive(parents):
        if image_t in parents: return 0
        newparents = parents + [image_t]
        tmphash = (0x5a5c6336cf623e9+ lcmtypes.image_request_t._get_hash_recursive(newparents)) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff)  + (tmphash>>63)) & 0xffffffffffffffff
        return tmphash
    _get_hash_recursive = staticmethod(_get_hash_recursive)
    _packed_fingerprint = None

    def _get_packed_fingerprint():
        if image_t._packed_fingerprint is None:
            image_t._packed_fingerprint = struct.pack(">Q", image_t._get_hash_recursive([]))
        return image_t._packed_fingerprint
    _get_packed_fingerprint = staticmethod(_get_packed_fingerprint)

