from typing import Mapping, Any, Union

import serial
from pexpect.spawnbase import SpawnBase

class SerialSpawn(SpawnBase):
    '''This is like pexpect.spawn but allows you to communicate with a serial port using
    pyserial, even on Windows.'''

    child_fd: Union[int, serial.Serial]

    def __init__(self,
                 # for serial.Serial
                 port,
                 serial_config: Mapping[str, Any] = {},
                 # for SpawnBase:
                 timeout=30,
                 maxread=2000,
                 searchwindowsize=None,
                 logfile=None,
                 encoding=None,
                 codec_errors='strict'):
        self._make_eof_and_intr()
        SpawnBase.__init__(self, timeout, maxread, searchwindowsize, logfile,
                           encoding=encoding, codec_errors=codec_errors)
        serial_config['timeout'] = 0
        self.child_fd = serial.Serial(port=port, **serial_config)
        self.own_fd = False
        self.closed = False
        self.name = self.child_fd.name

    def fileno(self):
        return self.child_fd.fileno()

    def close(self, *args):
        """Close the serial port.

        Calling this method a second time does nothing.
        """
        if self.child_fd == -1:
            return

        self.child_fd.flush()
        self.child_fd.close()
        self.child_fd = -1
        self.closed = True

    def isalive(self):
        '''This checks if the serial port is still valid.'''

        if self.child_fd == -1:
            return False
        else:
            return self.child_fd.isOpen()

    def terminate(self, force=False):  # pragma: no cover
        '''Deprecated and invalid. Just raises an exception.'''
        raise NotImplementedError('This method is not valid for serial port.')

    def flush(self):
        self.child_fd.flush()

    def send(self, s):
        "Write to serial port, return number of bytes written"
        s = self._coerce_send_string(s)
        self._log(s, 'send')

        b = self._encoder.encode(s, final=False)
        return self.child_fd.write(b)

    def sendline(self, s):
        "Write to serial port with trailing newline, return number of bytes written"
        s = self._coerce_send_string(s)
        return self.send(s + self.linesep)

    def write(self, s):
        "Write to serial port, return None"
        self.send(s)

    def writelines(self, sequence):
        "Call self.write() for each item in sequence"
        for s in sequence:
            self.write(s)

    def read_nonblocking(self, size=1, timeout=None):
        """
        Read from the serial port and return the result.

        The timeout argument is ignored, and returns immediately.
        """
        s = self.child_fd.read(size)
        s = self._decoder.decode(s, final=False)
        self._log(s, 'read')
        return s

    def _sendcontrol(self, char):
        '''Helper method that wraps send() with mnemonic access for sending control
        character to the child (such as Ctrl-C or Ctrl-D).  For example, to send
        Ctrl-G (ASCII 7, bell, '\a')::

            child.sendcontrol('g')
        '''

        char = char.lower()
        a = ord(char)
        if 97 <= a <= 122:
            a = a - ord('a') + 1
            byte = bytes([a])
            return self.child_fd.write(byte), byte
        d = {'@': 0, '`': 0,
             '[': 27, '{': 27,
             '\\': 28, '|': 28,
             ']': 29, '}': 29,
             '^': 30, '~': 30,
             '_': 31,
             '?': 127}
        if char not in d:
            return 0, b''

        byte = bytes([d[char]])
        return self.child_fd.write(byte), byte

    def sendcontrol(self, char):
        '''Helper method that wraps send() with mnemonic access for sending control
        character to the child (such as Ctrl-C or Ctrl-D).  For example, to send
        Ctrl-G (ASCII 7, bell, '\a')::

            child.sendcontrol('g')
        '''
        n, byte = self._sendcontrol(char)
        self._log(byte, 'send')
        return n

    def _make_eof_and_intr(self):
        try:
            from termios import CEOF, CINTR
            (intr, eof) = (CINTR, CEOF)
        except ImportError:
            #                         ^C, ^D
            (self._intr, self._eof) = (3, 4)

    def sendeof(self):
        '''This sends an EOF to the serial port. Normally Ctrl-D.'''
        byte = bytes([self._eof])
        return self.child_fd.write(byte), byte

    def sendintr(self):
        '''This sends a SIGINT to the serial port. Normally Ctrl-C.'''
        byte = bytes([self._intr])
        return self.child_fd.write(byte), byte
