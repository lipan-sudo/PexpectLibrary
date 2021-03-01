import signal
from typing import *
from robot.utils import (is_string, is_integer)
import pexpect


class PexpectLibrary(object):
    proc: Optional[pexpect.spawn]

    def __init__(self):
        self.proc = None

    def _spawn(self, do_spawn):
        try:
            # Kill the current active process
            if self.proc is not None:
                if self.proc.isalive():
                    self.proc.kill(signal.SIGKILL)
            self.proc = do_spawn()
            return self.proc
        except:
            self.proc = None
            raise

    def spawn(self, *args, **kwargs):
        self._spawn(lambda: pexpect.spawn(*args, **kwargs))

    def spawnu(self, *args, **kwargs):
        self._spawn(lambda: pexpect.spawnu(*args, **kwargs))

    def before(self):
        self._check_proc()
        return self.proc.before

    def after(self):
        self._check_proc()
        return self.proc.after

    def buffer(self):
        self._check_proc()
        return self.proc.buffer

    def _check_proc(self):
        if self.proc is None:
            raise PexpectLibraryProcessNotInitializedException('The process has not been created.')

    def _check_and_run(self, callback):
        self._check_proc()
        return callback()

    def expect(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.expect(*args, **kwargs))

    def expect_exact(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.expect_exact(*args, **kwargs))

    def expect_list(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.expect_list(*args, **kwargs))

    def compile_pattern_list(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.compile_pattern_list(*args, **kwargs))

    def send(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.send(*args, **kwargs))

    def send_line(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.sendline(*args, **kwargs))

    def write(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.write(*args, **kwargs))

    def write_lines(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.writelines(*args, **kwargs))

    def send_control(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.sendcontrol(*args, **kwargs))

    def send_eof(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.sendeof(*args, **kwargs))

    def send_sigint(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.sendintr(*args, **kwargs))

    def read(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.read(*args, **kwargs))

    def read_line(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.readline(*args, **kwargs))

    def read_nonblocking(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.read_nonblocking(*args, **kwargs))

    def eof(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.eof(*args, **kwargs))

    def interact(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.interact(*args, **kwargs))

    def get_logfile(self):
        self._check_proc()
        return self.proc.logfile

    def set_logfile(self, value):
        self._check_proc()
        self.proc.logfile = value

    def get_logfile_read(self):
        self._check_proc()
        return self.proc.logfile_read

    def set_logfile_read(self, value):
        self._check_proc()
        self.proc.logfile_read = value

    def get_logfile_send(self):
        self._check_proc()
        return self.proc.logfile_send

    def set_logfile_send(self, value):
        self._check_proc()
        self.proc.logfile = value

    def kill(self, sig=signal.SIGKILL):
        if not is_integer(sig):
            sig = signal.__dict__[str(sig)].value
        return self._check_and_run(lambda: self.proc.kill(sig))

    def terminate(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.terminate(*args, **kwargs))

    def is_alive(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.isalive(*args, **kwargs))

    def wait(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.wait(*args, **kwargs))

    def close(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.close(*args, **kwargs))

    def get_terminal_window_size(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.getwinsize(*args, **kwargs))

    def set_terminal_window_size(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.setwinsize(*args, **kwargs))

    def get_echo(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.getecho(*args, **kwargs))

    def set_echo(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.setecho(*args, **kwargs))

    def wait_no_echo(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.waitnoecho(*args, **kwargs))

    def wait_no_echo(self, *args, **kwargs):
        return self._check_and_run(lambda: self.proc.waitnoecho(*args, **kwargs))

    def get_pid(self):
        self._check_proc()
        return self.proc.pid

    def get_child_fd(self):
        self._check_proc()
        return self.proc.child_fd


def run(*args, **kwargs):
    return pexpect.run(*args, **kwargs)


def runu(*args, **kwargs):
    return pexpect.runu(*args, **kwargs)


def which(*args, **kwargs):
    return pexpect.which(*args, **kwargs)


def split_command_line(*args, **kwargs):
    return pexpect.split_command_line(*args, **kwargs)


class PexpectLibraryException(Exception):
    pass


class PexpectLibraryProcessNotInitializedException(PexpectLibraryException):
    pass


