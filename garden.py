from pathlib import Path
from datetime import datetime

WATER_MAX = 1
GROWTH_WATER_NEEDED = 1
RIPE_DAYS_FROM_SEED = 3


def create_garden(rows, cols):
    if rows <= 0 or cols <= 0:
        return []

    garden = []
    for _ in range(rows):
        row = []
        for _ in range(cols):
            row.append({"state": "empty", "crop": None, "water": 0, "days_as_seed": 0})
        garden.append(row)
    return garden


def is_in_bounds(garden, row, col):
    if not garden:
        return False
    return 0 <= row < len(garden) and 0 <= col < len(garden[0])


def get_cell(garden, row, col):
    if not is_in_bounds(garden, row, col):
        return None
    return garden[row][col]


def dig(garden, row, col):
    cell = get_cell(garden, row, col)
    if cell is None:
        return False
    if cell["state"] != "empty":
        return False

    cell["state"] = "hole"
    return True


def plant(garden, row, col, crop):
    cell = get_cell(garden, row, col)
    if cell is None:
        return False
    if cell["state"] != "hole":
        return False

    cell["state"] = "seed"
    cell["crop"] = crop
    cell["water"] = 0
    cell["days_as_seed"] = 0
    return True


def water(garden, row, col):
    cell = get_cell(garden, row, col)
    if cell is None:
        return False
    if cell["state"] != "seed":
        return False

    if cell["water"] < WATER_MAX:
        cell["water"] += 1
    return True


def advance_day(garden):
    if not garden:
        return True

    for row in garden:
        for cell in row:
            if cell["state"] == "seed" and cell["water"] >= GROWTH_WATER_NEEDED:
                cell["days_as_seed"] += 1
                if cell["days_as_seed"] >= RIPE_DAYS_FROM_SEED:
                    cell["state"] = "ripe"
            cell["water"] -= 1

    return True


def harvest(garden, row, col):
    cell = get_cell(garden, row, col)
    if cell is None:
        return None
    if cell["state"] != "ripe":
        return None

    harvested_crop = cell["crop"]
    cell["state"] = "empty"
    cell["crop"] = None
    cell["water"] = 0
    cell["days_as_seed"] = 0

    if harvested_crop != "tomato":
        print("[Info] The crop <name of the crop> has no file entry")

    if harvested_crop == "tomato":
        create_tomato_harvest_file()

    return harvested_crop

def create_tomato_harvest_file():
    ### Aufgabe 3: Wenn eine Tomate geerntet wird, soll der User über das Erstellen der tomato.txt Datei informiert werden.
    ### Der Satz "Created file 'tomato.txt' at <current datetime>" soll in der Konsole ausgegeben werden.
    ### Beispiel: Created file 'tomato.txt' at 18.05.2026 18:36:22

    harvests_dir = Path("harvests")
    harvests_dir.mkdir(exist_ok=True)
    target_file = harvests_dir / "tomato.txt"
    current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    line = f"harvested 1 tomato {current_datetime}\n"
    with target_file.open("a", encoding="utf-8") as file:
        file.write(line)

        print("Creaed file tomato.txt at <current datetie>")
    ### Aufgabe 3 Ende

