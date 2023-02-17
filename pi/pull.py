from subprocess import Popen, PIPE
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", "-r", help="abs path to root directory of this git repo"
    )
    args = parser.parse_args()

    p = Popen(
        [
            "git",
            "pull",
        ],
        cwd=args.root,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    print(str(out))
    print(str(err))


if __name__ == "__main__":
    main()
