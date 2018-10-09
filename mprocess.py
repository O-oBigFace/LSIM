from multiprocessing import Process
import serverCONFIG as scg
import time
from constructor import construct


def multi_run(function_name, num_of_process):
    total = scg.num_of_subjects
    quarter = int(total / num_of_process) + 1
    no_begin = scg.begin_index
    arglist = [(quarter * i + no_begin, quarter * (i + 1) + no_begin) for i in range(10)]
    print(arglist)
    """num 进程"""
    for i in range(1, num_of_process + 1):
        p = Process(target=function_name, args=arglist[i-1])
        p.start()
        time.sleep(30)


if __name__ == '__main__':
    multi_run(construct, 4)