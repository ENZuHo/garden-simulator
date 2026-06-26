from cli_view import GardenPrinter
from garden import advance_day, create_garden, dig, harvest, plant, water

CROPS = ["carrot", "tomato", "bean", "potato"]

COMMAND_COL_WIDTH = 18
DESCRIPTION_COL_WIDTH = 52
EXAMPLE_COL_WIDTH = 30


def parse_int(value):
    try:
        return int(value)
    except ValueError:
        return None


def split_text_to_lines(text, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current_line = words[0]

    i = 1
    while i < len(words):
        next_word = words[i]
        test_line = current_line + " " + next_word

        if len(test_line) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = next_word
        i += 1

    lines.append(current_line)
    return lines


def print_help_table():

    ### Aufgabe 2: Füge "quit" als Command Name hinzu, als Beschreibung "Exit the simulator" und als Beispiel "quit".
    rows = [
        ("show", "Display current day and garden grid", "show"),
        ("dig row col", "Dig a hole on an empty cell", "dig 1 2"),
        (
            "plant row col crop",
            "Plant a crop in a hole (available crops: " + ", ".join(CROPS) + ")",
            "plant 1 2 carrot",
        ),
        ("water row col", "Water a seed cell", "water 1 2"),
        ("day", "Advance simulation by one day", "day"),
        ("harvest row col", "Harvest a ripe crop", "harvest 1 2"),
        ("quit", "Exit the simulator", "quit")
    ]
    ### Ende Aufgabe 2

    print("Available commands:")
    print(
        f"{'Command':<{COMMAND_COL_WIDTH}} "
        f"{'Description':<{DESCRIPTION_COL_WIDTH}} "
        f"{'Example':<{EXAMPLE_COL_WIDTH}}"
    )
    print(
        f"{'-' * COMMAND_COL_WIDTH} "
        f"{'-' * DESCRIPTION_COL_WIDTH} "
        f"{'-' * EXAMPLE_COL_WIDTH}"
    )

    for command, description, example in rows:
        wrapped_description = split_text_to_lines(description, DESCRIPTION_COL_WIDTH)

        index = 0
        while index < len(wrapped_description):
            line = wrapped_description[index]
            if index == 0:
                left_command = command
                right_example = example
            else:
                left_command = ""
                right_example = ""

            print(
                f"{left_command:<{COMMAND_COL_WIDTH}} "
                f"{line:<{DESCRIPTION_COL_WIDTH}} "
                f"{right_example:<{EXAMPLE_COL_WIDTH}}"
            )
            index += 1


def main():
    garden = create_garden(5, 5)
    printer = GardenPrinter()
    current_day = 0

    print("Garden Simulator")
    print("Commands: show, dig r c, plant r c crop, water r c, day, harvest r c, help, quit")

    while True:
        line = input("> ").strip()
        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ("quit", "exit"):
            print("Bye")
            break

        if cmd == "help":
            print_help_table()
            continue

        if cmd == "show":
            print(f"Day: {current_day}")
            printer.print(garden)
            continue

        if cmd == "day":
            advance_day(garden)
            current_day += 1
            print(f"A day has passed. Current day: {current_day}")
            continue

        if cmd == "dig" and len(parts) == 3:
            row = parse_int(parts[1])
            col = parse_int(parts[2])
            if row is None or col is None:
                print("Coordinates must be numbers.")
            elif dig(garden, row, col):
                print("Dug a hole.")
            else:
                print("Action not allowed.")
            continue

        if cmd == "plant" and len(parts) >= 4:
            row = parse_int(parts[1])
            col = parse_int(parts[2])
            crop = " ".join(parts[3:])
            if row is None or col is None:
                print("Coordinates must be numbers.")
            elif crop not in CROPS:
                print(f"Unknown crop. Available crops: {', '.join(CROPS)}")
            elif plant(garden, row, col, crop):
                print(f"Planted {crop}.")
            else:
                print("Action not allowed.")
            continue

        if cmd == "water" and len(parts) == 3:
            row = parse_int(parts[1])
            col = parse_int(parts[2])
            if row is None or col is None:
                print("Coordinates must be numbers.")
            elif water(garden, row, col):
                print("Watered.")
            else:
                print("Action not allowed.")
            continue

        if cmd == "harvest" and len(parts) == 3:
            row = parse_int(parts[1])
            col = parse_int(parts[2])
            if row is None or col is None:
                print("Coordinates must be numbers.")
            else:
                crop = harvest(garden, row, col)
                if crop is None:
                    print("Action not allowed.")
                else:
                    print(f"Harvested: {crop}")
            continue

        print("Unknown command. Type 'help'.")


if __name__ == "__main__":
    main()