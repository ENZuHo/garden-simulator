import ast
import contextlib
import importlib
import io
import os
import re
import sys
import tempfile
import time
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


class TestFailure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise TestFailure(message)


def import_fresh(*module_names):
    for module_name in module_names:
        sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
    return [importlib.import_module(module_name) for module_name in module_names]


@contextlib.contextmanager
def temporary_working_directory():
    original_directory = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="garden-tests-") as temporary_directory:
        os.chdir(temporary_directory)
        try:
            yield Path(temporary_directory)
        finally:
            os.chdir(original_directory)


def prepare_ripe_crop(garden_module, crop):
    garden = garden_module.create_garden(1, 1)
    require(garden_module.dig(garden, 0, 0), "Could not dig the test cell.")
    require(garden_module.plant(garden, 0, 0, crop), f"Could not plant {crop}.")
    garden_module.get_cell(garden, 0, 0)["state"] = "ripe"
    return garden


def harvest_without_output(garden_module, garden):
    with contextlib.redirect_stdout(io.StringIO()):
        return garden_module.harvest(garden, 0, 0)


def test_task_1_tomato_cli_cycle():
    require(
        (PROJECT_DIR / "harvests" / "tomato.txt").is_file(),
        "The file harvests/tomato.txt does not exist.",
    )


def test_task_2_quit_help_entry():
    source = (PROJECT_DIR / "main.py").read_text(encoding="utf-8")
    tree = ast.parse(source, filename="main.py")
    help_function = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "print_help_table"
        ),
        None,
    )
    require(help_function is not None, "Function print_help_table() was not found.")

    rows_list = None
    for node in help_function.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "rows"
            and isinstance(node.value, ast.List)
        ):
            rows_list = node.value
            break

    require(rows_list is not None, "The rows list in print_help_table() was not found.")
    expected_row = ("quit", "Exit the simulator", "quit")
    rows = []
    for element in rows_list.elts:
        if isinstance(element, ast.Tuple) and len(element.elts) == 3:
            if all(
                isinstance(item, ast.Constant) and isinstance(item.value, str)
                for item in element.elts
            ):
                rows.append(tuple(item.value for item in element.elts))

    require(expected_row in rows, f"The help rows must contain {expected_row!r}.")


def test_task_3_tomato_creation_message():
    with temporary_working_directory():
        garden_module = import_fresh("garden")[0]
        garden = prepare_ripe_crop(garden_module, "tomato")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            harvested_crop = garden_module.harvest(garden, 0, 0)

        require(harvested_crop == "tomato", "Harvesting did not return tomato.")
        require(Path("harvests/tomato.txt").is_file(), "harvests/tomato.txt was not created.")
        require(
            re.search(
                r"Created file 'tomato\.txt' at \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}",
                output.getvalue(),
            ),
            "The required timestamped file creation message was not printed.",
        )


def test_task_4_non_tomato_message():
    with temporary_working_directory():
        garden_module = import_fresh("garden")[0]
        garden = prepare_ripe_crop(garden_module, "bean")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            harvested_crop = garden_module.harvest(garden, 0, 0)

        require(harvested_crop == "bean", "Harvesting did not return bean.")
        require(
            "[Info] The crop bean has no file entry." in output.getvalue(),
            "The required information message for bean was not printed.",
        )


def test_task_5_potato_growth():
    with temporary_working_directory():
        garden_module, main_module = import_fresh("garden", "main")
        require("potato" in main_module.CROPS, "potato is missing from main.py CROPS.")

        garden = garden_module.create_garden(1, 1)
        require(garden_module.dig(garden, 0, 0), "Could not dig the test cell.")
        require(garden_module.plant(garden, 0, 0, "potato"), "Could not plant potato.")

        require(garden_module.water(garden, 0, 0), "Could not water potato in cycle 1.")
        require(garden_module.advance_day(garden), "Could not advance day in cycle 1.")
        require(
            harvest_without_output(garden_module, garden) is None,
            "potato became ripe after only one water/day cycle.",
        )

        require(garden_module.water(garden, 0, 0), "Could not water potato in cycle 2.")
        require(garden_module.advance_day(garden), "Could not advance day in cycle 2.")
        require(
            harvest_without_output(garden_module, garden) == "potato",
            "potato was not harvestable after two water/day cycles.",
        )


def test_task_5_carrot_growth():
    with temporary_working_directory():
        garden_module = import_fresh("garden")[0]
        garden = garden_module.create_garden(1, 1)
        require(garden_module.dig(garden, 0, 0), "Could not dig the test cell.")
        require(garden_module.plant(garden, 0, 0, "carrot"), "Could not plant carrot.")

        for cycle in (1, 2):
            require(garden_module.water(garden, 0, 0), f"Could not water carrot in cycle {cycle}.")
            require(garden_module.advance_day(garden), f"Could not advance day in cycle {cycle}.")
            require(
                harvest_without_output(garden_module, garden) is None,
                f"carrot became ripe after only {cycle} water/day cycle(s).",
            )

        require(garden_module.water(garden, 0, 0), "Could not water carrot in cycle 3.")
        require(garden_module.advance_day(garden), "Could not advance day in cycle 3.")
        require(
            harvest_without_output(garden_module, garden) == "carrot",
            "carrot was not harvestable after three water/day cycles.",
        )


TESTS = [
    ("Task 1", "Complete tomato harvest cycle in the CLI", test_task_1_tomato_cli_cycle),
    ("Task 2", "Add quit to the help table", test_task_2_quit_help_entry),
    ("Task 3", "Print the tomato file creation message", test_task_3_tomato_creation_message),
    ("Task 4", "Print the non-tomato information message", test_task_4_non_tomato_message),
    ("Task 5", "Grow potato in two cycles", test_task_5_potato_growth),
    ("Task 5", "Keep carrot growth at three cycles", test_task_5_carrot_growth),
]


def color(text, code):
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR") is not None:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_unexpected_error(error):
    if isinstance(error, SyntaxError):
        location = f"line {error.lineno}" if error.lineno else "an unknown line"
        return f"SyntaxError at {location}: {error.msg}"
    message = str(error) or "No error message was provided."
    return f"{type(error).__name__}: {message}"


def run_tests():
    print("=" * 72)
    print("GARDEN SIMULATOR - ASSIGNMENT TESTS")
    print("=" * 72)
    print(f"Running {len(TESTS)} required tests...\n")

    passed = 0
    for task, description, test_function in TESTS:
        start_time = time.perf_counter()
        try:
            test_function()
        except TestFailure as error:
            duration = time.perf_counter() - start_time
            print(f"{color('[FAIL]', '31')} {task}: {description} ({duration:.2f}s)")
            print(f"       {error}")
        except Exception as error:
            duration = time.perf_counter() - start_time
            print(f"{color('[FAIL]', '31')} {task}: {description} ({duration:.2f}s)")
            print(f"       {format_unexpected_error(error)}")
        else:
            duration = time.perf_counter() - start_time
            passed += 1
            print(f"{color('[PASS]', '32')} {task}: {description} ({duration:.2f}s)")

    failed = len(TESTS) - passed
    print("\n" + "-" * 72)
    if failed == 0:
        print(color(f"ALL TESTS PASSED ({passed}/{len(TESTS)})", "32"))
        print("Your assignment implementation meets all tested requirements.")
    else:
        print(color(f"TESTS FAILED: {failed}  |  PASSED: {passed}/{len(TESTS)}", "31"))
        print("Review the messages above, update your code, and run the tests again.")
    print("-" * 72)
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
