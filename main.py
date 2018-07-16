from construct_virtual_document import construct
from mprocess import multi_run


if __name__ == '__main__':
    multi_run(construct, 4)
