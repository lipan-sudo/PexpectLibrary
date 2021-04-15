An (almost) complete and convenience Pexpect wrapper for Robot Framework, with extra functionalities.

Installation
---

The recommended installation method is using pip:

```
pip install PexpectLibrary
```

What is included in this library?
----------------

This library is almost complete. It provides the following classes to use:

* `pexpect.spawn`
* `pexpect.fdpexpect.fdspawn`
* `pexpect.popen_spawn.PopenSpawn`
* `SerialSpawn`, a class to interact on serial ports using pyserial, which is not in the pexpect library.

Note that not all keywords support all classes above.


Missing Functionalities
------------------------

Below is a list of missing functionalities from `pexpect`.

* `pexpect.run()`

  This function use `pexpect.spawn` which only work in *nix platforms. It's better to use the built-in
keyword `Process.Run Process`.
  
* `pexpect.spawn.interact()`
  
  This function is useless and difficult to implement due to Robot Framework's standard streams restriction. 

* class `pexpect.replwrap.REPLWrapper`
  
  The usage of this class is quite different from other classes. A new library with different name may better.
  This may be added in the future.

* class `pexpect.pxssh.pxssh`

  This class wraps the `ssh` command using ``pexpect.spawn`` . If you need a ssh client, an ssh client library might be better.

Let me know if you need these. They might be added in the future.
