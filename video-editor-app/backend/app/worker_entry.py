from rq import Worker
from .queue import redis_conn


def main():
    w = Worker(["renders"], connection=redis_conn)
    w.work()


if __name__ == "__main__":
    main()
