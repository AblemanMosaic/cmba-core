"""Single bounded read-only worker. Cancellation discards results, not thread termination.

There is never a second worker until the first exits. Tk operations stay on the main
thread. An interpreter thread is not a sandbox, CPU quota, or hostile-adapter isolation.
"""
import queue, threading, time
from cmba_core import Refusal
from cmba_core.errors import require
from .common import integer

class Jobs:
    def __init__(self, *, clock=time.monotonic):
        self.clock=clock;self.worker=None;self.queue=queue.Queue(maxsize=1)
        self.cancelled=False;self.expired=False;self.deadline=0;self.notified=False

    @property
    def busy(self):return self.worker is not None

    def start(self,fn, *, seconds=30):
        integer(seconds,1,120);require(not self.busy,'CMBA_K_JOB_BUSY')
        self.cancelled=False;self.expired=False;self.notified=False;self.deadline=self.clock()+seconds
        def run():
            try:item={'status':'RESULT','value':fn()}
            except Refusal as e:item={'status':'REFUSED','code':e.code}
            except Exception as e:item={'status':'REFUSED','code':'CMBA_K_INTERNAL_ERROR','exception_type':type(e).__name__}
            self.queue.put(item)
        self.worker=threading.Thread(target=run,name='CMBA-K1-read-only',daemon=True);self.worker.start()

    def cancel(self):
        self.cancelled=True

    def poll(self):
        if not self.busy:return None
        if self.clock()>=self.deadline:self.expired=True
        try:result=self.queue.get_nowait()
        except queue.Empty:
            if (self.cancelled or self.expired) and not self.notified:
                self.notified=True
                return {'status':'CANCELLED' if self.cancelled else 'TIMED_OUT','worker':'STILL_RUNNING_RESULT_WILL_BE_DISCARDED'}
            return None
        self.worker.join();self.worker=None
        if self.cancelled or self.expired:
            return {'status':'CANCELLED' if self.cancelled else 'TIMED_OUT','worker':'FINISHED_RESULT_DISCARDED'}
        return result
