import os
import signal
from datetime import timedelta
from typing import List, Union, Optional, Mapping, Callable, Any, Tuple, IO

import pexpect
from pexpect import fdpexpect, popen_spawn
from robot.utils import (timestr_to_secs)

from PexpectLibrary.serialspawn import SerialSpawn

__version__ = "0.2.0"


class PexpectLibrary(object):
    '''
    PexpetLibrary is a Pexpect wrapper for Robot Framework.

    This document explains how to use keywords provided by PexpectLibrary.
    For information about installation, support, and more, please visit the
    [https://github.com/lipan-sudo/PexpectLibrary|project pages].
    For more information about Robot Framework, see http://robotframework.org.

    The use of PexpectLibrary is as simple as Pexpect. Nearly all keywords has the same
    usage as the corresponding methods in Pexpect library, with a more convenience way.

    %TOC%

    = Active Process =

    All keywords in PexpectLibrary that need to interact with a process,
    should `Spawn` a new process first. This process will become the *active process*.
    These keywords no need to specify which process to interact with, they just
    interact with the current active process.

    The active process can be changed at anytime. The keywords `Current Active Process`
    and `Set Active Process` can be used to switch between active processes.

    = Time Format =

    All time arguments which has timedelta type in PexpectLibrary, can use the
    time format used in Robot Framework's standard library, like '5 seconds', etc.

    = Using Serial Ports =

    To interact with serial ports on Windows platform, use `Serial Spawn`.
    This keyword use pyserial to interact with serial ports. `Serial Spawn`
    can also be used in other platforms.

    For *nix platforms, `Fd Spawn` can also be used to interact with serial ports.
    '''

    ROBOT_LIBRARY_VERSION = __version__

    if os.name == 'nt':  # sys.platform == 'win32':
        _proc: Union[None, fdpexpect.fdspawn, SerialSpawn, popen_spawn.PopenSpawn]
    else:
        _proc: Union[None, pexpect.spawn, fdpexpect.fdspawn, SerialSpawn, popen_spawn.PopenSpawn]

    def __init__(self):
        self._proc = None

    def _timearg_to_seconds(self, value):
        if value is not None:
            if isinstance(value, timedelta):
                value = value.total_seconds()
            else:
                if isinstance(value, str) and (value.upper() == 'NONE'):
                    value = None
                else:
                    try:
                        # for -1, etc.
                        value = float(value)
                    except ValueError:
                        value = timestr_to_secs(value)
        return value

    def _optional_arg_conversion(self, value):
        # for rf < 4.0.1
        if value is not None:
            if isinstance(value, str) and (value.upper() == 'NONE'):
                value = None
        return value

    def _spawn(self, do_spawn):
        try:
            # Kill the current active process
            if self._proc is not None:
                if os.name != 'nt':  # sys.platform == 'win32':
                    if isinstance(self._proc, pexpect.spawn):
                        if self._proc.isalive():
                            self._proc.kill(signal.SIGKILL)
                            self._proc.wait()
                if isinstance(self._proc, (fdpexpect.fdspawn, SerialSpawn)):
                    if self._proc.isalive():
                        self._proc.close()
                if isinstance(self._proc, popen_spawn.PopenSpawn):
                    if self._proc.isalive():
                        self.kill()
                        self.wait()
            self._proc = do_spawn()
            return self._proc
        except:
            self._proc = None
            raise

    def spawn(self,
              command: str,
              args: List[str] = [],
              timeout: Optional[timedelta] = timedelta(seconds=30),  # require RF >= 4.0
              maxread: int = 2000,
              searchwindowsize: Optional[int] = None,
              logfile: Optional[IO] = None,
              cwd: Optional[str] = None,
              env: Optional[Mapping[str, str]] = None,
              ignore_sighup: bool = False,
              echo: bool = True,
              preexec_fn: Optional[Callable[[], Any]] = None,
              encoding: Optional[str] = 'utf-8',
              codec_errors: Any = 'strict',
              dimensions: Optional[Tuple[int, int]] = None,
              use_poll: bool = False):
        '''
        Spawn a new process, and set the active process to the new process.
        If current active process exists, it would be killed before spawning.

        The command parameter may be a string that
        includes a command and any arguments to the command. For example:

        | `Spawn` | /usr/bin/ftp |
        | `Spawn` | /usr/bin/ssh user@example.com |
        | `Spawn` | ls -latr /tmp |

        You may also construct it with a list of arguments like so:

        | `Spawn` | ls | [ '-latr', '/tmp' ] |

        After this the child application will be created and will be ready to
        talk to. For normal use, see `Expect` and `Send` and `Send Line`.

        Remember that Pexpect does NOT interpret shell meta characters such as
        redirect, pipe, or wild cards (``>``, ``|``, or ``*``). This is a
        common mistake.  If you want to run a command and pipe it through
        another command then you must also start a shell. For example:

        | `Spawn` | /bin/bash -c "ls -l > logs.txt" |
        | `Expect` | ${{ pexpect.EOF }} |

        The second form of spawn (where you pass a list of arguments) is useful
        in situations where you wish to spawn a command and pass it its own
        argument list. This can make syntax more clear. For example, the
        following is equivalent to the previous example:

        | `Spawn` | /bin/bash | [ '-c', 'ls -l > logs.txt' ] |
        | `Expect` | ${{ pexpect.EOF }} |

        The maxread attribute sets the read buffer size. This is maximum number
        of bytes that Pexpect will try to read from a TTY at one time. Setting
        the maxread size to 1 will turn off buffering. Setting the maxread
        value higher may help performance in cases where large amounts of
        output are read back from the child. This feature is useful in
        conjunction with searchwindowsize.

        When the keyword argument *searchwindowsize* is None (default), the
        full buffer is searched at each iteration of receiving incoming data.
        The default number of bytes scanned at each iteration is very large
        and may be reduced to collaterally reduce search cost.  After
        `Expect` returns, the full buffer attribute remains up to
        size *maxread* irrespective of *searchwindowsize* value.

        When the keyword argument ``timeout`` is specified,
        (default: *30*), then `pexpect.TIMEOUT` will be raised after the value
        specified has elapsed, in seconds, for any of the `Expect`
        family of keyword calls.  When None, `pexpect.TIMEOUT` will not be raised, and
        `Expect` may block indefinitely until match.

        The logfile member turns on or off logging. All input and output will
        be copied to the given file object. Set logfile to None to stop
        logging. This is the default. Set logfile to sys.stdout to echo
        everything to standard output. The logfile is flushed after each write.

        Example log input and output to a file:

        | `Spawn` | some_command |
        | `Set Logfile` | ${{ open('mylog.txt','wb') }} |

        Example log to stdout:

        | # In Python 3, we'll use the ``encoding`` argument to decode data |
        | # from the subprocess and handle it as unicode: |
        | `Spawn` | some_command | encoding=utf-8 | logfile=${{ sys.stdout }} |

        The logfile_read and logfile_send members can be used to separately log
        the input from the child and output sent to the child. Sometimes you
        don't want to see everything you write to the child. You only want to
        log what the child sends back. For example:

        | `Spawn` | some_command |
        | `Set Logfile Read` | ${{ sys.stdout }} |

        To separately log output sent to the child use logfile_send:

        | `Set Logfile Send` | ${fout} |

        If ``ignore_sighup`` is True, the child process will ignore SIGHUP
        signals. The default is False from Pexpect 4.0, meaning that SIGHUP
        will be handled normally by the child.

        The delaybeforesend helps overcome a weird behavior that many users
        were experiencing. The typical problem was that a user would `Expect` a
        "Password:" prompt and then immediately call `Send Line` to send the
        password. The user would then see that their password was echoed back
        to them. Passwords don't normally echo. The problem is caused by the
        fact that most applications print out the "Password" prompt and then
        turn off stdin echo, but if you send your password before the
        application turned off echo, then you get your password echoed.
        Normally this wouldn't be a problem when interacting with a human at a
        real keyboard. If you introduce a slight delay just before writing then
        this seems to clear up the problem. This was such a common problem for
        many users that I decided that the default pexpect behavior should be
        to sleep just before writing to the child application. 1/20th of a
        second (50 ms) seems to be enough to clear up the problem. You can set
        delaybeforesend to None to return to the old behavior.

        Note that `Spawn` is clever about finding commands on your path.
        It uses the same logic that `Which` uses to find executables.

        If you wish to get the exit status of the child you must call the
        `Close` keyword. The exit or signal status of the child will be stored
        in `exitstatus` attribute or `signalstatus` attribute. If the child exited normally
        then exitstatus will store the exit return code and signalstatus will
        be None. If the child was terminated abnormally with a signal then
        signalstatus will store the signal value and exitstatus will be None:

        | `Spawn` | some_command |
        | `Close` |
        | ${exitstatus} | `Get Exit Status` |
        | ${signalstatus} | `Get Signal Status` |
        | Log To Console | ${exitstatus}, ${signalstatus} |

        If you need more detail you can also read the `status` attribute which
        stores the status returned by os.waitpid. You can interpret this using
        os.WIFEXITED/os.WEXITSTATUS or os.WIFSIGNALED/os.TERMSIG.

        The echo attribute may be set to False to disable echoing of input.
        As a pseudo-terminal, all input echoed by the "keyboard" ( `Send`
        or `Send Line` ) will be repeated to output.  For many cases, it is
        not desirable to have echo enabled, and it may be later disabled
        using
        | `Set ECHO` | FALSE |
        followed by `Wait No ECHO`.  However, for some
        platforms such as Solaris, this is not possible, and should be
        disabled immediately on spawn.

        If preexec_fn is given, it will be called in the child process before
        launching the given command. This is useful to e.g. reset inherited
        signal handlers.

        The dimensions attribute specifies the size of the pseudo-terminal as
        seen by the subprocess, and is specified as a two-entry tuple (rows,
        columns). If this is unspecified, the defaults will apply.

        The use_poll attribute enables using select.poll() over select.select()
        for socket handling. This is handy if your system could have > 1024 fds
        '''
        encoding = self._optional_arg_conversion(encoding)
        timeout = self._timearg_to_seconds(timeout)
        return self._spawn(lambda: pexpect.spawn(command, args, timeout, maxread,
                                                 searchwindowsize, logfile, cwd, env,
                                                 ignore_sighup, echo, preexec_fn,
                                                 encoding, codec_errors, dimensions,
                                                 use_poll))

    def spawnu(self, *args, **kwargs):
        '''
        Deprecated. Same as `Spawn` .
        '''
        return self.spawn(*args, **kwargs)

    def fd_spawn(self,
                 fd,
                 timeout: Optional[timedelta] = timedelta(seconds=30),
                 maxread: int = 2000,
                 searchwindowsize: Optional[int] = None,
                 logfile: Optional[IO] = None,
                 encoding: Optional[str] = 'utf-8',
                 codec_errors: Any = 'strict',
                 use_poll: bool = False):
        '''This is like `Spawn` but allows you to supply your own open file
        descriptor. For example, you could use it to read through a file looking
        for patterns, or to control a modem or serial device.

        This takes a file descriptor (an int) or an object that support the
        fileno() method (returning an int). All Python file-like objects
        support fileno(). '''
        encoding = self._optional_arg_conversion(encoding)
        timeout = self._timearg_to_seconds(timeout)
        return self._spawn(lambda: fdpexpect.fdspawn(fd=fd, args=None, timeout=timeout, maxread=maxread,
                                                     searchwindowsize=searchwindowsize,
                                                     logfile=logfile, encoding=encoding, codec_errors=codec_errors,
                                                     use_poll=use_poll))

    def popen_spawn(self,
                    cmd,
                    timeout: Optional[timedelta] = timedelta(seconds=30),
                    maxread: int = 2000,
                    searchwindowsize: Optional[int] = None,
                    logfile: Optional[IO] = None,
                    cwd: Optional[str] = None,
                    env: Optional[Mapping[str, str]] = None,
                    encoding: Optional[str] = 'utf-8',
                    codec_errors: Any = 'strict',
                    preexec_fn: Optional[Callable[[], Any]] = None):
        '''Provides an interface like `Spawn` keyword using subprocess.Popen.'''
        encoding = self._optional_arg_conversion(encoding)
        timeout = self._timearg_to_seconds(timeout)
        return self._spawn(lambda: popen_spawn.PopenSpawn(cmd=cmd,
                                                          timeout=timeout,
                                                          maxread=maxread,
                                                          searchwindowsize=searchwindowsize,
                                                          logfile=logfile,
                                                          cwd=cwd,
                                                          env=env,
                                                          encoding=encoding,
                                                          codec_errors=codec_errors,
                                                          preexec_fn=preexec_fn
                                                          ))

    def serial_spawn(self,
                     # for serial.Serial
                     port: str,
                     serial_config: Mapping[str, Any] = {},
                     # for SpawnBase:
                     timeout: Optional[timedelta] = timedelta(seconds=30),
                     maxread: int = 2000,
                     searchwindowsize: Optional[int] = None,
                     logfile: Optional[IO] = None,
                     encoding: Optional[str] = 'utf-8',
                     codec_errors: Any = 'strict'):
        '''This is like `Fd Spawn` but allows you to communicate with a serial port using
        pyserial, even on Windows. Arguments pass to serial.Serial() can be specified using
        *serial_config*.

        Example:

        | `Serial Spawn` | COM11 | { 'baudrate': 115200 } |

        '''
        encoding = self._optional_arg_conversion(encoding)
        timeout = self._timearg_to_seconds(timeout)
        return self._spawn(lambda: SerialSpawn(port=port, serial_config=serial_config, timeout=timeout, maxread=maxread,
                                               searchwindowsize=searchwindowsize, logfile=logfile, encoding=encoding,
                                               codec_errors=codec_errors))

    def current_active_process(self):
        '''Returns current active process.'''
        return self._proc

    def set_active_process(self, proc=None):
        '''Returns current active process, and switch active process to *proc* .

        If *proc* is None (default), clear current active process. This can be used to avoid
        current active process to be closed automatically before spawning a new process. For
        example:

        | `Set Active Process` |
        | `Spawn` | ... |
        '''
        current = self._proc
        self._proc = proc
        return current

    def get_status(self):
        '''Returns the `status' attribute.'''
        self._check_proc()
        return self._proc.status

    def get_exit_status(self):
        '''Returns the `exitstatus' attribute.'''
        self._check_proc()
        return self._proc.exitstatus

    def get_signal_status(self):
        '''Returns the `signalstatus' attribute.'''
        self._check_proc()
        return self._proc.signalstatus

    def set_delay_after_read(self, value: Union[None, float, timedelta]):
        '''Change the value of `delayafterread' attribute.'''
        self._check_proc()
        self._proc.delayafterread = self._timearg_to_seconds(value)

    def get_delay_after_read(self):
        '''Returns the `delayafterread' attribute.'''
        self._check_proc()
        return self._proc.delayafterread

    def set_delay_before_send(self, value: Union[None, float, timedelta]):
        '''Change the value of `delaybeforesend' attribute.'''
        self._check_proc()
        self._proc.delaybeforesend = self._timearg_to_seconds(value)

    def get_delay_before_send(self):
        '''Returns the `delaybeforesend' attribute.'''
        self._check_proc()
        return self._proc.delaybeforesend

    def set_delay_after_close(self, value: Optional[timedelta]):
        '''Change the value of `delayafterclose' attribute.'''
        self._check_proc()
        self._proc.delayafterclose = self._timearg_to_seconds(value)

    def get_delay_after_close(self):
        '''Returns the `delayafterclose' attribute.'''
        self._check_proc()
        return self._proc.delayafterclose

    def set_delay_after_terminate(self, value: Optional[timedelta]):
        '''Change the value of `delayafterterminate' attribute.'''
        self._check_proc()
        self._proc.delayafterterminate = self._timearg_to_seconds(value)

    def get_delay_after_terminate(self):
        '''Returns the `delayafterterminate' attribute.'''
        self._check_proc()
        return self._proc.delayafterterminate

    def set_line_separator(self, value):
        '''Change the value of `linesep' attribute (line separator).'''
        self._check_proc()
        self._proc.linesep = value

    def get_line_separator(self):
        '''Returns the `linesep' attribute (line separator).'''
        self._check_proc()
        return self._proc.linesep

    def set_timeout(self, value: Optional[timedelta]):
        '''Change the value of `timeout' attribute.'''
        self._check_proc()
        self._proc.timeout = self._timearg_to_seconds(value)

    def get_timeout(self):
        '''Returns the `timeout' attribute.'''
        self._check_proc()
        return self._proc.timeout

    def get_maxread(self):
        '''Returns the `maxread' attribute.'''
        self._check_proc()
        return self._proc.maxread

    def set_maxread(self, value: int):
        '''Change the value of `maxread' attribute.'''
        self._check_proc()
        self._proc.maxread = value

    def match(self):
        '''Returns the `match' attribute.'''
        self._check_proc()
        return self._proc.match

    def match_groups(self):
        '''Returns the matched groups.'''
        self._check_proc()
        return self._proc.match.groups()

    def before(self):
        '''Returns the `before' attribute.'''
        self._check_proc()
        return self._proc.before

    def after(self):
        '''Returns the `after' attribute.'''
        self._check_proc()
        return self._proc.after

    def buffer(self):
        '''Returns the `buffer' attribute.'''
        self._check_proc()
        return self._proc.buffer

    def _check_proc(self):
        if self._proc is None:
            raise PexpectLibraryProcessNotInitializedException('The process has not been created.')

    def _check_and_run(self, callback):
        self._check_proc()
        return callback()

    def expect(self,
               pattern,
               timeout: Union[None, float, timedelta] = -1,
               searchwindowsize: int = -1,
               **kwargs):
        '''This seeks through the stream until a pattern is matched. The
        pattern is overloaded and may take several types. The pattern can be a
        StringType, pexpect.EOF, pexpect.TIMEOUT, a compiled re, or a list of any of those types.
        Strings will be compiled to re types. This returns the index into the
        pattern list. If the pattern was not a list this returns index 0 on a
        successful match. This may raise exceptions for EOF or TIMEOUT. To
        avoid the EOF or TIMEOUT exceptions add pexpect.EOF or pexpect.TIMEOUT to the pattern
        list. That will cause expect to match an EOF or TIMEOUT condition
        instead of raising an exception.

        If you pass a list of patterns and more than one matches, the first
        match in the stream is chosen. If more than one pattern matches at that
        point, the leftmost in the pattern list is chosen. For example:

            | # the input is 'foobar' |
            | ${index} | `Expect` | ${{ ['bar', 'foo', 'foobar'] }} |
            | # returns 1('foo') even though 'foobar' is a "better" match |

        Please note, however, that buffering can affect this behavior, since
        input arrives in unpredictable chunks. For example:

            | # the input is 'foobar' |
            | ${index} | `Expect` | ${{ ['foobar', 'foo'] }} |
            | # returns 0('foobar') if all input is available at once, |
            | # but returns 1('foo') if parts of the final 'bar' arrive late |

        When a match is found for the given pattern, the
        attribute *match* becomes an re.MatchObject result.  Should a pexpect.EOF
        or pexpect.TIMEOUT pattern match, then the match attribute will be an instance
        of that exception class.  The pairing before and after attributes are views of the data preceding and following
        the matching pattern.  On general exception, attribute
        *before* is all data received up to the exception, while *match* and
        *after* attributes are value None.

        When the keyword argument timeout is -1 (default), then pexpect.TIMEOUT will
        raise after the default value specified by the class timeout
        attribute. When None, pexpect.TIMEOUT will not be raised and may block
        indefinitely until match.

        When the keyword argument searchwindowsize is -1 (default), then the
        value specified by the maxread attribute is used.

        A list entry may be pexpect.EOF or pexpect.TIMEOUT instead of a string. This will
        catch these exceptions and return the index of the list entry instead
        of raising the exception. The attribute 'after' will be set to the
        exception type. The attribute 'match' will be None. This allows you to
        write code like this:

                | ${index} | `Expect` | ${{ ['good', 'bad', pexpect.EOF, pexpect.TIMEOUT] }} |
                | Run Keyword If | ${index} == 0 | Do Something |
                | ... | ELSE IF | ${index} == 1 | Do Something Else |
                | ... | ELSE IF | ${index} == 2 | Do Some Other Thing |
                | ... | ELSE IF | ${index} == 3 | Do Something Completely Different |

        You can also just expect the pexpect.EOF if you are waiting for all output of a
        child to finish. For example:

                | `Spawn` | /bin/ls |
                | `Expect` | ${{ pexpect.EOF }} |
                | ${before} | `Before` |
                | Log To Console | ${before} |

        If you are trying to optimize for speed then see `Expect List` .
        '''
        timeout = self._timearg_to_seconds(timeout)
        return self._check_and_run(lambda: self._proc.expect(pattern, timeout, searchwindowsize, False, **kwargs))

    def expect_exact(self, pattern_list, timeout: Union[None, float, timedelta] = -1,
                     searchwindowsize: int = -1, **kwargs):
        '''This is similar to `Expect` , but uses plain string matching instead
        of compiled regular expressions in 'pattern_list'. The 'pattern_list'
        may be a string; a list or other sequence of strings; or pexpect.TIMEOUT and
        pexpect.EOF .

        This call might be faster than `Expect` for two reasons: string
        searching is faster than RE matching and it is possible to limit the
        search to just the end of the input buffer.

        This keyword is also useful when you don't want to have to worry about
        escaping regular expression characters that you want to match.
        '''
        timeout = self._timearg_to_seconds(timeout)
        return self._check_and_run(lambda: self._proc.expect_exact(pattern_list, timeout, searchwindowsize,
                                                                   False, **kwargs))

    def expect_list(self, pattern_list, timeout: Union[None, float, timedelta] = -1, searchwindowsize: int = -1,
                    **kwargs):
        '''This takes a list of compiled regular expressions and returns the
        index into the pattern_list that matched the child output. The list may
        also contain pexpect.EOF or pexpect.TIMEOUT(which are not compiled regular
        expressions). This keyword is similar to the `Expect` keyword except that
        `Expect List` does not recompile the pattern list on every call. This
        may help if you are trying to optimize for speed, otherwise just use
        the `Expect` keyword.  This is called by `Expect`.
        '''
        timeout = self._timearg_to_seconds(timeout)
        return self._check_and_run(lambda: self._proc.expect_list(pattern_list, timeout, searchwindowsize,
                                                                  False, **kwargs))

    def compile_pattern_list(self, patterns):
        '''This compiles a pattern-string or a list of pattern-strings.
        Patterns must be a StringType, pexpect.EOF, pexpect.TIMEOUT, SRE_Pattern, or a list of
        those. Patterns may also be None which results in an empty list (you
        might do this if waiting for an EOF or TIMEOUT condition without
        expecting any pattern).

        This is used by `Expect` when calling `Expect List`. Thus `Expect` is
        nothing more than:


        | cpl = self.compile_pattern_list(pl)
        | return self.expect_list(cpl, timeout)

        If you are using `Expect` within a loop it may be more
        efficient to compile the patterns first and then call `Expect List`.
        This avoid calls in a loop to `Compile Pattern List`:

             | ${cpl} | `Compile Pattern List` | my_pattern |
             | FOR | some conditions ... |
             | | ... |
             | | ${i} | `Expect List` | ${cpl} | timeout |
             | | ... |
             | END |

        '''
        return self._check_and_run(lambda: self._proc.compile_pattern_list(patterns))

    def send(self, s):
        '''Sends string ``s`` to the child process, returning the number of
        bytes written. If a logfile is specified, a copy is written to that
        log.

        The default terminal input mode is canonical processing unless set
        otherwise by the child process. This allows backspace and other line
        processing to be performed prior to transmitting to the receiving
        program. As this is buffered, there is a limited size of such buffer.

        On Linux systems, this is 4096 (defined by N_TTY_BUF_SIZE). All
        other systems honor the POSIX.1 definition PC_MAX_CANON -- 1024
        on OSX, 256 on OpenSolaris, and 1920 on FreeBSD.

        This value may be discovered using fpathconf(3):

            | Log To Console | ${{ os.fpathconf(0, 'PC_MAX_CANON') }} |
        ==> 256

        On such a system, only 256 bytes may be received per line. Any
        subsequent bytes received will be discarded. BEL (``'\\a'``) is then
        sent to output if IMAXBEL (termios.h) is set by the tty driver.
        This is usually enabled by default.  Linux does not honor this as
        an option -- it behaves as though it is always set on.

        Canonical input processing may be disabled altogether by executing
        a shell, then stty(1), before executing the final program:

            | `Spawn` | /bin/bash | echo=False |
            | `Send Line` | stty -icanon |
            | `Send Line` | base64 |
            | `Send Line` | ${{ 'x' * 5000 }} |
        '''
        return self._check_and_run(lambda: self._proc.send(s))

    def send_line(self, s=''):
        '''Wraps `Send` , sending string ``s`` to child process, with
        ``os.linesep`` automatically appended. Returns number of bytes
        written.  Only a limited number of bytes may be sent for each
        line in the default terminal mode, see docstring of `Send` .
        '''
        return self._check_and_run(lambda: self._proc.sendline(s))

    def write(self, s):
        '''
        This is similar to `Send` except that there is no return value.
        '''
        return self._check_and_run(lambda: self._proc.write(s))

    def write_lines(self, sequence: List):
        '''This calls `Write` for each element in the sequence. The sequence
        can be any iterable object producing strings, typically a list of
        strings. This does not add line separators. There is no return value.
        '''
        return self._check_and_run(lambda: self._proc.writelines(sequence))

    def send_control(self, char):
        '''Helper keyword that wraps `Send` with mnemonic access for sending control
        character to the child (such as Ctrl-C or Ctrl-D).  For example, to send
        Ctrl-G (ASCII 7, bell, '\\a'):

            | `Send Control` | g |

        See also, `Send SIGINT` and `Send EOF` .
        '''
        return self._check_and_run(lambda: self._proc.sendcontrol(char))

    def send_eof(self):
        '''This sends an EOF to the child. This sends a character which causes
        the pending parent output buffer to be sent to the waiting child
        program without waiting for end-of-line. If it is the first character
        of the line, the `Read` in the user program returns 0, which signifies
        end-of-file. This means to work as expected a `Send EOF` has to be
        called at the beginning of a line. This keyword does not send a newline.
        It is the responsibility of the caller to ensure the eof is sent at the
        beginning of a line. '''
        return self._check_and_run(lambda: self._proc.sendeof())

    def send_sigint(self):
        '''This sends a SIGINT to the child. It does not require
        the SIGINT to be the first character on a line. '''
        return self._check_and_run(lambda: self._proc.sendintr())

    def read(self, size: int = -1):
        '''This reads at most "size" bytes from the file (less if the read hits
        EOF before obtaining size bytes). If the size argument is negative or
        omitted, read all data until EOF is reached. The bytes are returned as
        a string object. An empty string is returned when EOF is encountered
        immediately. '''
        return self._check_and_run(lambda: self._proc.read(size))

    def read_line(self, size: int = -1):
        '''This reads and returns one entire line. The newline at the end of
        line is returned as part of the string, unless the file ends without a
        newline. An empty string is returned if EOF is encountered immediately.
        This looks for a newline as a CR/LF pair (\\r\\n) even on UNIX because
        this is what the pseudotty device returns. So contrary to what you may
        expect you will receive newlines as \\r\\n.

        If the size argument is 0 then an empty string is returned. In all
        other cases the size argument is ignored, which is not standard
        behavior for a file-like object. '''
        return self._check_and_run(lambda: self._proc.readline(size))

    def read_nonblocking(self, size: int = 1, timeout: Union[None, float, timedelta] = -1):
        '''This reads at most size characters from the child application. It
        includes a timeout. If the read does not complete within the timeout
        period then a pexpect.TIMEOUT exception is raised. If the end of file is read
        then an pexpect.EOF exception will be raised.  If a logfile is specified, a
        copy is written to that log.

        If timeout is None then the read may block indefinitely.
        If timeout is -1 then the timeout attribute is used. If timeout is 0
        then the child is polled and if there is no data immediately ready
        then this will raise a pexpect.TIMEOUT exception.

        The timeout refers only to the amount of time to read at least one
        character. This is not affected by the 'size' parameter, so if you call
        | `Read Nonblocking` | size=100 | timeout=30 |
        and only one character is
        available right away then one character will be returned immediately.
        It will not wait for 30 seconds for another 99 characters to come in.

        On the other hand, if there are bytes available to read immediately,
        all those bytes will be read (up to the buffer size). So, if the
        buffer size is 1 megabyte and there is 1 megabyte of data available
        to read, the buffer will be filled, regardless of timeout.

        This is a wrapper around os.read(). It uses select.select() or
        select.poll() to implement the timeout. '''
        timeout = self._timearg_to_seconds(timeout)
        return self._check_and_run(lambda: self._proc.read_nonblocking(size, timeout))

    def eof(self):
        '''This returns True if the pexpect.EOF exception was ever raised.
        '''
        return self._check_and_run(lambda: self._proc.eof())

    def get_logfile(self):
        '''Returns the `logfile' attribute.'''
        self._check_proc()
        return self._proc.logfile

    def set_logfile(self, value):
        '''Change the value of `logfile' attribute.'''
        self._check_proc()
        self._proc.logfile = value

    def get_logfile_read(self):
        '''Returns the `logfile_read' attribute.'''
        self._check_proc()
        return self._proc.logfile_read

    def set_logfile_read(self, value):
        '''Change the value of `logfile_read' attribute.'''
        self._check_proc()
        self._proc.logfile_read = value

    def get_logfile_send(self):
        '''Returns the `logfile_send' attribute.'''
        self._check_proc()
        return self._proc.logfile_send

    def set_logfile_send(self, value):
        '''Change the value of `logfile_send' attribute.'''
        self._check_proc()
        self._proc.logfile_send = value

    def kill(self, sig: Union[int, str] = signal.SIGKILL if os.name != 'nt' else signal.SIGTERM):
        '''
        This sends the given signal to the child application. In keeping
        with UNIX tradition it has a misleading name. It does not necessarily
        kill the child unless you send the right signal.

        ``sig`` is the number of the signal, also, can be the name of the signal. The following 2 lines are equal:

        | `Kill` | SIGKILL |
        | `Kill` | 9 |

        The default value of ``sig`` is SIGTERM on Windows, and SIGKILL on other platforms.
        '''
        try:
            sig = int(sig)
        except ValueError:
            sig = signal.__dict__[str(sig)].value
        return self._check_and_run(lambda: self._proc.kill(sig))

    def terminate(self, force: bool = False):
        '''This forces a child process to terminate. It starts nicely with
        SIGHUP and SIGINT. If "force" is True then moves onto SIGKILL. This
        returns True if the child was terminated. This returns False if the
        child could not be terminated. '''
        return self._check_and_run(lambda: self._proc.terminate(force))

    def is_alive(self):
        '''This tests if the child process is running or not. This is
        non-blocking. If the child was terminated then this will read the
        exitstatus or signalstatus of the child. This returns True if the child
        process appears to be running or False if not. It can take literally
        SECONDS for Solaris to return the right status. '''
        return self._check_and_run(lambda: self._proc.isalive())

    def wait(self):
        '''This waits until the child exits. This is a blocking call. This will
        not read any data from the child, so this will block forever if the
        child has unread output and has terminated. In other words, the child
        may have printed output then called exit(), but, the child is
        technically still alive until its output is read by the parent.

        This keyword is non-blocking if `Wait` has already been called
        previously or `Is Alive` keyword returns False.  It simply returns
        the previously determined exit status.
        '''

        return self._check_and_run(lambda: self._proc.wait())

    def close(self, force: bool = True):
        '''This closes the connection with the child application. Note that
        calling `Close` more than once is valid. This emulates standard Python
        behavior with files. Set force to True if you want to make sure that
        the child is terminated (SIGKILL is sent if the child ignores SIGHUP
        and SIGINT). '''
        return self._check_and_run(lambda: self._proc.close(force))

    def get_terminal_window_size(self):
        '''This returns the terminal window size of the child tty. The return
        value is a tuple of (rows, cols). '''
        return self._check_and_run(lambda: self._proc.getwinsize())

    def set_terminal_window_size(self, rows: int, cols: int):
        '''This sets the terminal window size of the child tty. This will cause
        a SIGWINCH signal to be sent to the child. This does not change the
        physical window size. It changes the size reported to TTY-aware
        applications like vi or curses -- applications that respond to the
        SIGWINCH signal. '''
        return self._check_and_run(lambda: self._proc.setwinsize(rows, cols))

    def get_echo(self):
        '''This returns the terminal echo mode. This returns True if echo is
        on or False if echo is off. Child applications that are expecting you
        to enter a password often set ECHO False. See `Wait No ECHO` .

        Not supported on platforms where ``isatty()`` returns False.  '''
        return self._check_and_run(lambda: self._proc.getecho())

    def set_echo(self, state: bool):
        '''This sets the terminal echo mode on or off. Note that anything the
        child sent before the echo will be lost, so you should be sure that
        your input buffer is empty before you call `Set ECHO` . For example, the
        following will work as expected:

            | `Spawn` | cat | # Echo is on by default. |
            | `Send Line` | 1234 | # We expect see this twice from the child... |
            | `Expect` | 1234 | # ... once from the tty echo... |
            | `Expect` | 1234 | # ... and again from cat itself. |
            | `Set Echo` | FALSE | # Turn off tty echo |
            | `Send Line` | abcd | # We will set this only once (echoed by cat). |
            | `Send Line` | wxyz | # We will set this only once (echoed by cat) |
            | `Expect` | abcd |
            | `Expect` | wxyz |

        The following WILL NOT WORK because the lines sent before the setecho
        will be lost:

            | `Spawn` | cat |
            | `Send Line` | 1234 |
            | `Set Echo` | FALSE | # Turn off tty echo |
            | `Send Line` | abcd | # We will set this only once (echoed by cat). |
            | `Send Line` | wxyz | # We will set this only once (echoed by cat) |
            | `Expect` | 1234 |
            | `Expect` | 1234 |
            | `Expect` | abcd |
            | `Expect` | wxyz |


        Not supported on platforms where ``isatty()`` returns False.
        '''
        return self._check_and_run(lambda: self._proc.setecho(state))

    def wait_no_echo(self, timeout: Union[None, float, timedelta] = -1):
        '''This waits until the terminal ECHO flag is set False. This returns
        True if the echo mode is off. This returns False if the ECHO flag was
        not set False before the timeout. This can be used to detect when the
        child is waiting for a password. Usually a child application will turn
        off echo mode when it is waiting for the user to enter a password. For
        example, instead of expecting the "password:" prompt you can wait for
        the child to set ECHO off:

            | `Spawn` | ssh user@example.com |
            | `Wait No Echo` |
            | `Send Line` | mypassword |

        If timeout==-1 then this keyword will use the value in timeout attribute.
        If timeout==None then this keyword to block until ECHO flag is False.
        '''
        timeout = self._timearg_to_seconds(timeout)
        return self._check_and_run(lambda: self._proc.waitnoecho(timeout))

    def get_pid(self):
        '''Returns the `pid' of current active process.'''
        self._check_proc()
        return self._proc.pid

    def get_child_fd(self):
        '''Returns the child `fd' of current active process.'''
        self._check_proc()
        return self._proc.child_fd

    @staticmethod
    def which(filename: str, env: Optional[Mapping[str, str]] = None):
        '''This takes a given filename; tries to find it in the environment path;
        then checks if it is executable. This returns the full path to the filename
        if found and executable. Otherwise this returns None.

        If `env` is not specified, use `os.environ` instead.

        Example:

        | ${path} | `Which` | java | { 'PATH': '/usr/lib/jvm/java-1.14.0-openjdk-amd64/bin' } |
        | Log To Console | ${path} |

        '''
        return pexpect.which(filename, env)


class PexpectLibraryException(Exception):
    pass


class PexpectLibraryProcessNotInitializedException(PexpectLibraryException):
    pass
