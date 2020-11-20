import random


def random_string():
    chars = 'abc''def''ghi''jkl''mno''pqr''stu''vwx''yz1234567890'
    return ''.join((random.choice(chars) for _ in range(4)))
