import schedule
import time
from wf import Sweeper, Sentry


def main():
    sweeper = Sweeper("sweeper")
    sentry = Sentry("sentry")

    schedule.every(10).seconds.do(sweeper.run_task)
    schedule.every(10).seconds.do(sentry.run_task)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
