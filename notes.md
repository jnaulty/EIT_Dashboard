error when running `pip install -r requirements.txt`
```
Collecting pyobjc-framework-ScreenSaver==5.1 (from PyObjC==5.1->-r requirements.txt (line 12))
  Downloading https://files.pythonhosted.org/packages/86/e4/fdd5ed0687cc722d2c0d30037a848cb0d497439b41ce63764f3ada012542/pyobjc-framework-ScreenSaver-5.1.tar.gz
    Complete output from command python setup.py egg_info:
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/tmp/pip-build-_lkbj7gt/pyobjc-framework-ScreenSaver/setup.py", line 21, in <module>
        extra_link_args=['-framework', 'ScreenSaver']),
      File "/tmp/pip-build-_lkbj7gt/pyobjc-framework-ScreenSaver/pyobjc_setup.py", line 389, in Extension
        os_level = get_os_level()
      File "/tmp/pip-build-_lkbj7gt/pyobjc-framework-ScreenSaver/pyobjc_setup.py", line 203, in get_os_level
        pl = plistlib.readPlist('/System/Library/CoreServices/SystemVersion.plist')
      File "/usr/lib/python3.6/plistlib.py", line 162, in readPlist
        with _maybe_open(pathOrFile, 'rb') as fp:
      File "/usr/lib/python3.6/contextlib.py", line 81, in __enter__
        return next(self.gen)
      File "/usr/lib/python3.6/plistlib.py", line 120, in _maybe_open
        with open(pathOrFile, mode) as fp:
    FileNotFoundError: [Errno 2] No such file or directory: '/System/Library/CoreServices/SystemVersion.plist'

    ----------------------------------------
Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-_lkbj7gt/pyobjc-framework-ScreenSaver/
```

solution: use [environment-markers](https://www.python.org/dev/peps/pep-0508/#environment-markers) sys_platform value

on ubuntu 18.04 requires apt get install python3-tk
Also requires the package `bluez`

more errors around objc

```
python simdata.py               
Traceback (most recent call last):
  File "simdata.py", line 19, in <module>
    import OpenEIT.dashboard
  File "/home/jnaulty/workspace/foss/EIT_Dashboard/OpenEIT/dashboard/__init__.py", line 1, in <module>
    from .controller import Controller
  File "/home/jnaulty/workspace/foss/EIT_Dashboard/OpenEIT/dashboard/controller.py", line 12, in <module>
    import OpenEIT.backend
  File "/home/jnaulty/workspace/foss/EIT_Dashboard/OpenEIT/backend/__init__.py", line 5, in <module>
    from .serialhandler import SerialHandler #, parse_line
  File "/home/jnaulty/workspace/foss/EIT_Dashboard/OpenEIT/backend/serialhandler.py", line 21, in <module>
    import objc

```

`No module named 'objc' error on Linux`
```
python offline.py 
Traceback (most recent call last):
  File "offline.py", line 12, in <module>
    import OpenEIT.dashboard
  File "/home/jnaulty/workspace/foss/EIT_Dashboard/OpenEIT/dashboard/__init__.py", line 1, in <module>
    from .controller import Controller
  File "/home/jnaulty/workspace/foss/EIT_Dashboard/OpenEIT/dashboard/controller.py", line 12, in <module>
    import OpenEIT.backend
  File "/home/jnaulty/workspace/foss/EIT_Dashboard/OpenEIT/backend/__init__.py", line 5, in <module>
    from .serialhandler import SerialHandler #, parse_line
  File "/home/jnaulty/workspace/foss/EIT_Dashboard/OpenEIT/backend/serialhandler.py", line 21, in <module>
    import objc
ModuleNotFoundError: No module named 'objc'

```

`lungwgel.bin` file not found

```
python offline.py 
Traceback (most recent call last):
  File "offline.py", line 33, in <module>
    text_file = open("lungwgel.bin", "r")
FileNotFoundError: [Errno 2] No such file or directory: 'lungwgel.bin'
(virty) ➜  EIT_Dashboard git:(master) ✗ git grep lungwgel
offline.py:text_file = open("lungwgel.bin", "r")
(virty) ➜  EIT_Dashboard git:(master) ✗ find . -name 'lungwgel.bin'        
(virty) ➜  EIT_Dashboard git:(master) ✗        
```


new notes
-------

imaging: http://localhost:8050/Imaging
set to 32 bits (would be nice to check data set when reading file)
step through data.

errors out
