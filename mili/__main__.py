import sys
import webbrowser


def main():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
    sys.stdout.flush()

    if len(sys.argv) <= 1:
        print("ERROR: missing command 'guide'")
        return
    if len(sys.argv) > 2:
        print("ERROR: too many commands")
        return
    if sys.argv[1] != "guide":
        print(f"ERROR: wrong command '{sys.argv[1]}', expected 'guide'")
        return

    url = "https://github.com/damusss/mili/blob/main/guide/guide.md"
    print(f"Opening guide at '{url}'")
    webbrowser.open(url)


if __name__ == "__main__":
    main()
