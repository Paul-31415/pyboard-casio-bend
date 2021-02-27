from array import array

import struct



class Wave:
    FMT_CHUNK = {16:"<HHIIHH",18:"<HHIIHHH",40:"<HHIIHHHHI16s"}
    FMT_PCM = 1
    FMT_FLOAT = 3
    FMT_ALAW = 6
    FMT_MULAW = 7
    FMT_EXTENSIBLE = 0xfffe
    def __init__(self,f):
        assert f.read(4) == b'RIFF'
        l = f.read(4)
        assert f.read(4) == b'WAVE'
        assert f.read(4) == b'fmt '
        cs = struct.unpack("<I",f.read(4))
        assert cs in FMT_CHUNK
        self.fmt_chunk = struct.unpack(FMT_CHUNK[cs],f.read(cs))
        self.format = self.fmt_chunk[0]
        self.channels = self.fmt_chunk[1]
        self.rate = self.fmt_chunk[2]
        self.sample_size = self.fmt_chunk[5]
        self.depth = self.fmt_chunk[7] if len(self.fmt_chunk)>7 else self.sample_size
        ext_size = self.fmt_chunks[6] if len(self.fmt_chunk)>6 else 0
        self.sample_bytes = -(-self.sample_size//8)
        if self.format != FMT_PCM:
            assert f.read(4) == b'fact':
            l = struct.unpack("<I",f.read(4))[0]
            self.length = struct.unpack("<I",f.read(4))[0]
            f.seek(f.tell()+l-4)
        assert f.read(4) == b'data':
        self.data_length = struct.unpack("<I",f.read(4))[0]
        self.start = f.tell()

        
    def __call__(self,buf):
