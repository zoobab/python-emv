# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals


class RAPDU(object):
    ''' Response Application Protocol Data Unit

        Defined in: EMV 4.3 Book 3 section 6.3.3
    '''

    @classmethod
    def unmarshal(cls, data):
        assert len(data) > 1
        sw1 = data[-2]
        sw2 = data[-1]

        assert sw1 not in (0x61, 0x6C)  # should be handled by the transport layer.

        if sw1 == 0x90 and sw2 == 0x00:
            obj = SuccessResponse()
        elif sw1 in (0x62, 0x63):
            obj = WarningResponse()
        elif sw1 in (0x69, 0x6A):
            obj = ErrorResponse()
        else:
            assert False
        obj.sw1 = sw1
        obj.sw2 = sw2
        obj.data = data[:-2]

        return obj

    def get_status(self):
        return "SW1: %02x, SW2: %02x" % (self.sw1, self.sw2)

    def __repr__(self):
        res = '<%s: "%s"' % (self.__class__.__name__, self.get_status())
        if len(self.data) > 0:
            data = ' '.join(['%02x' % i for i in self.data])
            res += ', data: ' + data
        return res + '>'


class SuccessResponse(RAPDU):
    def get_status(self):
        return "Process completed"


class WarningResponse(RAPDU):
    def get_status(self):
        if self.sw1 == 0x62 and self.sw2 == 0x83:
            return "State of non-volatile memory unchanged; selected file invalidated"
        elif self.sw1 == 0x63 and self.sw2 == 0x00:
            return "State of non-volatile memory changed; authentication failed"
        elif self.sw1 == 0x63 and self.sw2 & 0xC0 == 0xC0:
            return "State of non-volatile memory changed; counter is %i" % (self.sw2 & ~0xC0)


class ErrorResponse(RAPDU):
    ERRORS = {
        (0x69, 0x83): 'Command not allowed; authentication method blocked',
        (0x69, 0x84): 'Command not allowed; referenced data invalidated',
        (0x69, 0x85): 'Command not allowed; conditions of use not satisfied',
        (0x6A, 0x81): 'Wrong parameter(s) P1 P2; function not supported',
        (0x6A, 0x82): 'Wrong parameter(s) P1 P2; file not found',
        (0x6A, 0x83): 'Wrong parameter(s) P1 P2; record not found',
        (0x6A, 0x88): 'Referenced data (data objects) not found'
    }

    def get_status(self):
        return self.ERRORS.get((self.sw1, self.sw2))