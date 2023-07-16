import pendulum


def get_timestamp()->int:
    return int(pendulum.now().float_timestamp * 1000)