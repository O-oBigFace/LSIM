from multiprocessing import Process
import multiprocessing
import serverCONFIG as scg


def multi_run(function_name, num_of_process):
    total = scg.num_of_subjects
    quarter = int(total / num_of_process) + 1
    no_begin = scg.begin_index
    arglist = [
               (no_begin, quarter + no_begin),
               (quarter + no_begin, quarter * 2 + no_begin),
               (quarter * 2 + no_begin, quarter * 3 + no_begin),
               (quarter * 3 + no_begin, quarter * 4 + no_begin),
               (quarter * 4 + no_begin, quarter * 5 + no_begin),
               (quarter * 5 + no_begin, quarter * 6 + no_begin),
               ]
    """num 进程"""
    for i in range(1, num_of_process + 1):
        p = Process(target=function_name, args=arglist[i-1])
        p.start()
