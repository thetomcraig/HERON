import random
import logging


def clear_set(set_to_clear):
    [x.delete() for x in set_to_clear]
