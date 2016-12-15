from subprocess import Popen
import subprocess


class Im(object):
    @staticmethod
    def execute(cmd, listener):
        if listener is not None and not isinstance(listener, ImListener):
            raise TypeError('invalid type of listener')

        print ('1')
        # run command
        p = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

        (out, err) = p.communicate()
        return p.returncode, out, err

    @staticmethod
    def execute(cmd):
        # run command
        p = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

        (out, err) = p.communicate()
        return p.returncode, out, err
