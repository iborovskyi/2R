from distutils.core import setup
import py2exe, sys, os
import pygame.mixer # fix mixer

# Font fix. Hopefully...
dlls = ["libfreetype-6.dll", "libogg-0.dll", "sdl_ttf.dll"]
origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
       if os.path.basename(pathname).lower() in dlls:
               return 0
       return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL


setup_dict = dict(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True, "includes":["pygame.mixer"]}},
    windows = [{'script': 'revenant.py',
    "icon_resources": [(1, "icon.ico")]}],
    zipfile = None,
)

setup(**setup_dict)
setup(**setup_dict)
