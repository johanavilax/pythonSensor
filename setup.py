from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = {"packages": ["eventlet","dns",'engineio', 'socketio', 'flask_socketio', 'threading', 'time', 'queue','jinja2'], 'include_files':"config"}

setup(name='menzies',
      version = '1',
      description = 'menzies',
      options = dict(build_exe = buildOptions),
      executables = [Executable("finalServer.py")],)
