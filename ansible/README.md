cat unit.json | curl -X PUT --data-binary @- --unix-socket /var/run/unit/control.sock http://localhost/config/

ezid@uc3-ezidarks-stg01:17:13:00:~/install/arksorg-site/ansible$ pyenv prefix
/ezid/.pyenv/versions/3.11.6

-------------------------------
Fri Oct 13 06:05:44 PM PDT 2023

current errors:

```
2023/10/13 17:42:32 [info] 593206#593206 "rslv" application started
Python path configuration:
  PYTHONHOME = '/ezid/.pyenv/versions/3.11.6'
  PYTHONPATH = (not set)
  program name = 'python3'
  isolated = 1
  environment = 0
  user site = 0
  safe_path = 1
  import site = 1
  is in build tree = 0
  stdlib dir = '/ezid/.pyenv/versions/3.11.6/lib64/python3.11'
  sys._base_executable = '/usr/bin/python3'
  sys.base_prefix = '/ezid/.pyenv/versions/3.11.6'
  sys.base_exec_prefix = '/ezid/.pyenv/versions/3.11.6'
  sys.platlibdir = 'lib64'
  sys.executable = '/usr/bin/python3'
  sys.prefix = '/ezid/.pyenv/versions/3.11.6'
  sys.exec_prefix = '/ezid/.pyenv/versions/3.11.6'
  sys.path = [
    '/ezid/.pyenv/versions/3.11.6/lib64/python311.zip',
    '/ezid/.pyenv/versions/3.11.6/lib64/python3.11',
    '/ezid/.pyenv/versions/3.11.6/lib64/python3.11/lib-dynload',
  ]
2023/10/13 17:42:32 [alert] 593206#593206 Failed to initialise config
```

noticed my pyenv has not lib64:

ezid@uc3-ezidarks-stg01:17:48:16:~/.pyenv/versions/3.11.6$ ll
total 16
drwxr-xr-x. 2 ezid ezid 4096 Oct 13 17:16 bin
drwxr-xr-x. 3 ezid ezid 4096 Oct 13 11:54 include
drwxr-xr-x. 4 ezid ezid 4096 Oct 13 11:54 lib
drwxr-xr-x. 3 ezid ezid 4096 Oct 13 11:54 share
ezid@uc3-ezidarks-stg01:17:48:17:~/.pyenv/versions/3.11.6$ ln -s lib lib64
ezid@uc3-ezidarks-stg01:17:48:29:~/.pyenv/versions/3.11.6$ ll
total 16
drwxr-xr-x. 2 ezid ezid 4096 Oct 13 17:16 bin
drwxr-xr-x. 3 ezid ezid 4096 Oct 13 11:54 include
drwxr-xr-x. 4 ezid ezid 4096 Oct 13 11:54 lib
lrwxrwxrwx. 1 ezid ezid    3 Oct 13 17:48 lib64 -> lib
drwxr-xr-x. 3 ezid ezid 4096 Oct 13 11:54 share


Now I'm back to:

2023/10/13 17:48:51 [alert] 594594#594594 Python failed to import module "rslv.app"
Traceback (most recent call last):
  File "/ezid/arksorg/resolver/rslv/app.py", line 10, in <module>
    import logging.config
  File "/ezid/.pyenv/versions/3.11.6/lib64/python3.11/logging/config.py", line 30, in <module>
    import logging.handlers
  File "/ezid/.pyenv/versions/3.11.6/lib64/python3.11/logging/handlers.py", line 26, in <module>
    import io, logging, socket, os, pickle, struct, time, re
  File "/ezid/.pyenv/versions/3.11.6/lib64/python3.11/socket.py", line 54, in <module>
    import os, sys, io, selectors
  File "/ezid/.pyenv/versions/3.11.6/lib64/python3.11/selectors.py", line 11, in <module>
    import math
ImportError: /ezid/.pyenv/versions/3.11.6/lib64/python3.11/lib-dynload/math.cpython-311-x86_64-linux-gnu.so: undefined symbol: _PyModule_Add


The few refs on google suggest python version issues. poetry clashing with 3.11.5

https://github.com/python-poetry/poetry/issues/8452

