import sys
import subprocess
import signal

try:
    from shutil import which
except ImportError:
    from backports.shutil_which import which


def assert_binary_presence(binary_name):
    if not which(binary_name):
        print('|ERROR| Cannot find %s. Please install it and check your PATH variable.'
              % binary_name, file=sys.stderr)
        sys.exit(10)


def execute_command(cmd, debug=False):
    if isinstance(cmd, list):
        cmd = ' '.join(str(c) for c in cmd)
    try:
        proc = subprocess.Popen(args=cmd, shell=True, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, universal_newlines=True)
        if debug:
            print('Executing:')
            print(cmd)
        stdout, stderr = proc.communicate()
        print(stdout, file=sys.stdout, end='')
        print(stderr, file=sys.stderr, end='')
        exit_code = proc.returncode
        if exit_code < 0:
            print('|ERROR|', 'Tried executing:')
            print('|ERROR|', cmd)
            print('|ERROR|', 'Exited with signal: %s' % signal.Signals(-exit_code).name)
            sys.exit(1)
        if debug:
            print('Exited with code: %s' % exit_code)
            sys.exit(exit_code)
    except OSError as ex:
        print('|ERROR| Sorry something went horribly wrong when executing\n%s' % cmd,
              file=sys.stderr)
        print('|ERROR| You may want to report the error to us.', file=sys.stderr)
        raise ex
