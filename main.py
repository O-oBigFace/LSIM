from constructor import construct
from mprocess import multi_run
import warnings
warnings.filterwarnings('ignore')


if __name__ == '__main__':
    multi_run(construct, 4)
