from multiprocessing import Process

from ditmewibu import run as ditmewibu
from h3ck3r import run as h3ck3r
from hnvw import run as hnvw

Process(target=ditmewibu).start()
Process(target=h3ck3r).start()
Process(target=hnvw).start()
