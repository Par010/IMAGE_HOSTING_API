import random
import string


def generate_radom_string(length=10):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
