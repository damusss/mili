import sys
import webbrowser


def main():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
    sys.stdout.flush()

    if len(sys.argv) <= 1:
        print("ERROR: missing command")
        return
    if len(sys.argv) > 2:
        print("ERROR: too many commands")
        return

    command = sys.argv[1]
    help_cmds = ["help", "-h", "--help", "-help", "--h"]
    version_cmds = ["version", "ver", "-v", "--ver", "-version", "--version", "-ver"]

    if (
        command
        not in [
            "guide",
            "changelog",
            "demo",
        ]
        + help_cmds
        + version_cmds
    ):
        print(
            f"ERROR: wrong command '{sys.argv[1]}', expected one of the following: 'guide', 'changelog', 'demo', 'help', 'version'"
        )
        return

    if command == "guide":
        url = "https://github.com/damusss/mili/blob/main/guide/guide.md"
        print(f"Opening guide at '{url}'")
        webbrowser.open(url)
    elif command == "changelog":
        url = "https://github.com/damusss/mili/blob/main/CHANGELOG.md"
        print(f"Opening changelog at '{url}'")
        webbrowser.open(url)
    elif command == "demo":
        from mili.demo import demo

        demo.main()
    elif command in version_cmds:
        import mili

        print(f"MILI {mili.VERSION_STR}")
    elif command in help_cmds:
        print("MILI CLI")
        print("py -m mili guide: open the MILI guide")
        print("py -m mili changelog: open the MILI changelog")
        print("py -m mili version/-v: print the installed MILI version")
        print("py -m mili help/-h: show this message")


if __name__ == "__main__":
    main()
