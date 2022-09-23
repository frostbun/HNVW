from multiprocessing import Process

from ditmewibu import run as ditmewibu
from h3ck3r import run as h3ck3r
from hnvm import run as hnvm

Process(target=ditmewibu).start()
Process(target=h3ck3r).start()
Process(target=hnvm).start()
