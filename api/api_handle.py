# Auto generate at 2016-09-29T18:05:27.406533.
# By proto-ext
# DO NOT EDIT

import math
import struct

int_1_byte = struct.Struct('>B')
int_2_byte = struct.Struct('>H')
int_4_byte = struct.Struct('>I')

INTEGER_32_MAX = 2 ** 31 - 1
INTEGER_32_MIN = - 2 ** 31


class _Package(object):
    pass


class _Message(object):
    __slots__ = []
    FULL_NAME = ''

## PROTOCOL START ##

class API(_Package):
    class Common(_Package):
        class ExtraReturn(_Message):
            __slots__ = ["char_id", "msgs", ]
            FULL_NAME = "API.Common.ExtraReturn"
            
            def __init__(self):
                self.char_id = None
                self.msgs = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
    class Party(_Package):
        class Create(_Message):
            __slots__ = ["server_id", "char_id", "party_level", ]
            FULL_NAME = "API.Party.Create"
            
            def __init__(self):
                self.server_id = None
                self.char_id = None
                self.party_level = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class CreateDone(_Message):
            __slots__ = ["ret", "extras", ]
            FULL_NAME = "API.Party.CreateDone"
            
            def __init__(self):
                self.ret = None
                self.extras = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class Start(_Message):
            __slots__ = ["server_id", "char_id", "party_level", "members", ]
            FULL_NAME = "API.Party.Start"
            
            def __init__(self):
                self.server_id = None
                self.char_id = None
                self.party_level = None
                self.members = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class StartDone(_Message):
            __slots__ = ["ret", "extras", ]
            FULL_NAME = "API.Party.StartDone"
            
            def __init__(self):
                self.ret = None
                self.extras = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class Buy(_Message):
            __slots__ = ["server_id", "char_id", "party_level", "buy_id", "members", ]
            FULL_NAME = "API.Party.Buy"
            
            def __init__(self):
                self.server_id = None
                self.char_id = None
                self.party_level = None
                self.buy_id = None
                self.members = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class BuyDone(_Message):
            __slots__ = ["ret", "extras", "buy_name", "item_name", "item_amount", ]
            FULL_NAME = "API.Party.BuyDone"
            
            def __init__(self):
                self.ret = None
                self.extras = None
                self.buy_name = None
                self.item_name = None
                self.item_amount = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class End(_Message):
            __slots__ = ["server_id", "char_id", "party_level", "members", ]
            FULL_NAME = "API.Party.End"
            
            def __init__(self):
                self.server_id = None
                self.char_id = None
                self.party_level = None
                self.members = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class EndDone(_Message):
            __slots__ = ["ret", "extras", "talent_id", ]
            FULL_NAME = "API.Party.EndDone"
            
            def __init__(self):
                self.ret = None
                self.extras = None
                self.talent_id = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
    class Session(_Package):
        class PartyInfo(_Message):
            __slots__ = ["max_buy_times", "remained_create_times", "remained_join_times", "talent_id", ]
            FULL_NAME = "API.Session.PartyInfo"
            
            def __init__(self):
                self.max_buy_times = None
                self.remained_create_times = None
                self.remained_join_times = None
                self.talent_id = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class Parse(_Message):
            __slots__ = ["session", ]
            FULL_NAME = "API.Session.Parse"
            
            def __init__(self):
                self.session = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
        class ParseDone(_Message):
            __slots__ = ["ret", "extras", "server_id", "char_id", "flag", "name", "partyinfo", ]
            FULL_NAME = "API.Session.ParseDone"
            
            def __init__(self):
                self.ret = None
                self.extras = None
                self.server_id = None
                self.char_id = None
                self.flag = None
                self.name = None
                self.partyinfo = None
                
            def __str__(self):
                f = _Formatter()
                f.format_message(self)
                return f.get_content()
        
## PROTOCOL END ##

# TODO using c extension
def encode(obj):
    encoder = _Encoder()
    encoder.encode_message(obj)
    return ''.join(encoder.byte_chunks)

def decode(message):
    decoder = _Decoder(message)
    decoder.decode()
    return decoder.obj

class _Formatter(object):
    def __init__(self):
        self.indent = -1
        self.lines = []

    def get_content(self):
        return '\n'.join(self.lines)

    def make_blank(self):
        return ' ' * 2 * self.indent

    def add_line(self, content=''):
        line = '{0}{1}'.format(self.make_blank(), content)
        self.lines.append(line)

    def format_message(self, obj):
        self.indent += 1
        line = '< {0} >'.format(obj.FULL_NAME)
        self.add_line(line)

        self.indent += 1

        for field in obj.__slots__:
            line = '{0}: '.format(field)
            self.add_line(line)

            value = getattr(obj, field)
            self.format_value(value)

        self.add_line()
        self.indent -= 2

    def format_value(self, value):
        if isinstance(value, _Message):
            self.format_message(value)
        elif isinstance(value, (list, tuple)):
            self.add_line('[')
            self.indent += 1
            self.add_line()

            for v in value:
                self.format_value(v)

            self.indent -= 1
            self.add_line(']')
        else:
            self.lines[-1] = self.lines[-1] + ' {0} '.format(repr(value))


class _Decoder(object):
    def __init__(self, message):
        self.obj = None
        self.message = message
        self.index = 0

    def decode(self):
        if int_1_byte.unpack(self.message[self.index])[0] != 131:
            raise ValueError("Invalid version header")

        self.index += 1
        self.obj = self.decode_value()

    def decode_message(self, arity):
        if int_1_byte.unpack(self.message[self.index])[0] != 100:
            raise ValueError("Invalid Atom header")

        name = self.decode_value()
        name_list = name.split('.')

        obj = globals()[name_list[0]]
        for n in name_list[1:]:
            obj = getattr(obj, n)

        obj = obj()
        for i in range(arity-1):
            key = obj.__slots__[i]
            value = self.decode_value()
            setattr(obj, key, value)

        return obj

    def decode_value(self):
        tag = int_1_byte.unpack(self.message[self.index])[0]
        self.index += 1

        if tag == 97:
            value = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1
            return value

        if tag == 98:
            value = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4
            return value

        if tag == 70:
            value = struct.unpack('>d', self.message[self.index: self.index + 8])[0]
            self.index += 8
            return value

        if tag == 100:
            length = int_2_byte.unpack(self.message[self.index: self.index + 2])[0]
            self.index += 2
            value = struct.unpack('{0}s'.format(length), self.message[self.index: self.index + length])[0]
            self.index += length

            if value == "undefined":
                return None
            if value == "true":
                return True
            if value == "false":
                return False

            return value

        if tag == 104:
            arity = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1
            return self.decode_message(arity)

        if tag == 105:
            arity = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4
            return self.decode_message(arity)

        if tag == 107:
            length = int_2_byte.unpack(self.message[self.index: self.index + 2])[0]
            self.index += 2
            value = []
            for i in range(length):
                value.append(struct.unpack('>c', self.message[self.index])[0])
                self.index += 1

            return ''.join(value)

        if tag == 109:
            length = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4
            value = struct.unpack('{0}s'.format(length), self.message[self.index: self.index + length])[0]
            self.index += length
            return value

        if tag == 110:
            n = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1
            sign = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1

            value = 0
            for i in range(n):
                d = int_1_byte.unpack(self.message[self.index])[0]
                self.index += 1

                value += d * 256 ** i

            if sign == 0:
                return value
            return -value

        if tag == 111:
            n = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4
            sign = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1

            value = 0
            for i in range(n):
                d = int_1_byte.unpack(self.message[self.index])[0]
                self.index += 1

                value += d * 256 ** i

            if sign == 0:
                return value
            return -value

        if tag == 108:
            length = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4

            value = []
            for i in range(length):
                value.append(self.decode_value())

            tail = int_1_byte.unpack(self.message[self.index])[0]
            if tail == 106:
                self.index += 1

            return value

        raise ValueError("UnSupported tag: {0}".format(tag))


class _Encoder(object):
    def __init__(self):
        self.byte_chunks = _encode_version()

    def encode_message(self, obj):
        self.byte_chunks.extend(
            _encode_tuple_header(len(obj.__slots__) + 1, obj.FULL_NAME)
        )

        for field in obj.__slots__:
            value = getattr(obj, field)
            self.encode_value(value)

    def encode_value(self, value):
        if value is None:
            self.byte_chunks.extend(_encode_atom("undefined"))
        elif value is True:
            self.byte_chunks.extend(_encode_atom("true"))
        elif value is False:
            self.byte_chunks.extend(_encode_atom("false"))

        elif isinstance(value, (int, long)):
            self.byte_chunks.extend(_encode_integer(value))
        elif isinstance(value, float):
            self.byte_chunks.extend(_encode_float(value))
        elif isinstance(value, (basestring, bytearray)):
            self.byte_chunks.extend(_encode_binary(value))
        elif isinstance(value, (list, tuple)):
            self.byte_chunks.extend(_encode_list_header(len(value)))

            for v in value:
                self.encode_value(v)

            self.byte_chunks.extend(_encode_list_tail())
        elif isinstance(value, _Message):
            self.encode_message(value)


def _encode_integer(value):
    if 0 <= value <= 255:
        return [int_1_byte.pack(97), int_1_byte.pack(value)]

    if INTEGER_32_MIN <= value <= INTEGER_32_MAX:
        return [int_1_byte.pack(98), int_4_byte.pack(value)]

    if value < 0:
        sign = 1
        value = -value
    else:
        sign = 0

    n = int(math.ceil(math.log(value, 256)))
    seq = []
    for i in range(n - 1, -1, -1):
        d, value = divmod(value, 256 ** i)
        seq.insert(0, d)

    chunks = []
    if n > 255:
        chunks.append(int_1_byte.pack(111))
        chunks.append(int_4_byte.pack(n))
    else:
        chunks.append(int_1_byte.pack(110))
        chunks.append(int_1_byte.pack(n))

    chunks.append(int_1_byte.pack(sign))
    for d in seq:
        chunks.append(int_1_byte.pack(d))

    return chunks


def _encode_float(value):
    return [
        int_1_byte.pack(70),
        struct.pack('>d', value)
    ]


def _encode_binary(value):
    if isinstance(value, unicode):
        value = value.encode('utf-8')

    length = len(value)
    return [
        int_1_byte.pack(109),
        int_4_byte.pack(length),
        struct.pack('{0}s'.format(length), value)
    ]


def _encode_atom(value):
    length = len(value)
    return [
        int_1_byte.pack(100),
        int_2_byte.pack(length),
        struct.pack('{0}s'.format(length), value)
    ]


def _encode_version():
    return [
        int_1_byte.pack(131)
    ]


def _encode_tuple_header(arity, name):
    if arity < 255:
        chunks = [
            int_1_byte.pack(104),
            int_1_byte.pack(arity),
        ]
    else:
        chunks = [
            int_1_byte.pack(105),
            int_4_byte.pack(arity),
        ]

    chunks.extend(_encode_atom(name))
    return chunks


def _encode_list_header(length):
    return [
        int_1_byte.pack(108),
        int_4_byte.pack(length)
    ]


def _encode_list_tail():
    return [
        int_1_byte.pack(106)
    ]


