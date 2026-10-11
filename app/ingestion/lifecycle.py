"""One monotonic teardown deadline and bounded command TERM/KILL supervision."""
import subprocess
import time

from .types import IngestionError


class Teardown:
    def __init__(self, clock=time.monotonic):
        self.clock, self.deadline = clock, None

    def begin(self):
        if self.deadline is None:
            self.deadline = self.clock() + 45
        return self.deadline

    def remaining(self):
        return max(0, self.begin() - self.clock())

    def phase(self, seconds):
        return min(self.begin(), self.clock() + seconds)


def guarded_command(command, deadline, clock=time.monotonic, factory=subprocess.Popen):
    available = deadline - clock()
    if available <= 0:
        raise IngestionError('cleanup_failed')
    process = factory(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    reserve = min(5, available / 2)
    try:
        output, _errors = process.communicate(timeout=max(0, deadline - clock() - reserve))
        if process.returncode:
            raise IngestionError('cleanup_failed')
        return output
    except subprocess.TimeoutExpired as error:
        process.terminate()
        try:
            process.communicate(timeout=max(0, min(2, (deadline - clock()) / 2)))
        except subprocess.TimeoutExpired:
            process.kill()
            try:
                process.communicate(timeout=max(0, min(3, deadline - clock())))
            except subprocess.TimeoutExpired:
                pass
        raise IngestionError('cleanup_failed') from error
