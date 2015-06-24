import os
import subprocess
import sys


class GitIgnoreAwareListdir(object):
    def __init__(self, listdir=os.listdir):
        self.listdir = listdir
        self.git_process = subprocess.Popen(
            ["git", "check-ignore", "--stdin", '--non-matching', '-vz'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            env={"GIT_FLUSH": "1"})
        self.encoding = sys.getfilesystemencoding()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def __call__(self, path):
        for item in self.listdir(path):
            fullpath = os.path.join(path, item)
            self.git_process.stdin.write(self._encode(fullpath) + b'\0')
            self.git_process.stdin.flush()
            (source, linunum, pattern, pathname) = [
                self._fetch_null_terminated_value()
                for _ in range(4)]
            if source:
                print('ignoring %s' % fullpath)
                continue
            yield item

    def close(self):
        self.git_process.kill()

    def _fetch_null_terminated_value(self):
        val = b''
        while True:
            c = self.git_process.stdout.read(1)
            if c == b'\0':
                return val
            val += c

    def _encode(self, text):
        return text.encode(self.encoding, "surrogateescape")
