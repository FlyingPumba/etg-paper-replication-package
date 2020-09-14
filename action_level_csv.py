import datetime
import os

import cfg
from command import run_cmd, run_simple_cmd

column_names = [
    "Subject",
    "Repetition",
    "Test index",
    "Action index",

    "Successful in ETG?",

    "Number of different pixels",
    "Total pixels",
    "Percentage of different pixels",
    "Different screenshots?",

    "Home number of different pixels",
    "Home percentage of different pixels",
    "Home?"
]

fuzz_factor = 20
screenshots_pixel_percentage_threshold = 0.05

def build():
    total_pixels = None
    home_screenshot = f"{cfg.wd}/home.png"

    csv_lines = []

    # add column names
    csv_lines.append(",".join(list(map(lambda c: f"\"{c}\"", column_names))))

    # process each folder in results
    output, error, return_code = run_cmd(f"ls {cfg.results_path}")
    package_names = output.strip("\n").split("\n")

    for package_name in package_names:
        # process each repetition available
        output, error, return_code = run_cmd(f"ls {cfg.results_path}/{package_name}/")
        if output == "":
            # no sub-folders, skip it
            continue

        repetitions = output.strip("\n").split("\n")
        for repetition in repetitions:
            results_path = os.path.join(cfg.results_path, package_name, str(repetition))

            # gather ETG data
            failing_actions_by_test_index = parse_failing_actions(package_name, repetition)

            # parse screenshots
            output, error, return_code = run_cmd(f"ls {results_path}/etg/")
            etg_test_folders = list(filter(lambda f: "ETGTestCase" in f, output.strip("\n").split("\n")))

            for test_folder in etg_test_folders:
                test_index = test_folder.split("ETGTestCase")[1]
                failing_actions = failing_actions_by_test_index[test_index]

                output, error, return_code = run_cmd(f"ls {results_path}/etg/{test_folder}/screenshots/{test_folder}*.png")
                etg_screenshots = output.strip("\n").split("\n")

                output, error, return_code = run_cmd(f"ls {results_path}/mate/screenshots/MATE_{test_index}_*.png")
                mate_screenshots = output.strip("\n").split("\n")

                if len(etg_screenshots) != len(mate_screenshots):
                    raise Exception(f"La cantidad de screenshots para el test case numero {test_index} del package" +
                                    f" {package_name} difiere entre MATE ({len(mate_screenshots)}) y " +
                                    f"ETG ({len(etg_screenshots)}")

                screenshots_comparison_folder = f"{results_path}/etg/{test_folder}/screenshots-comparison"
                run_simple_cmd(f"mkdir -p {screenshots_comparison_folder}")
                run_simple_cmd(f"rm {screenshots_comparison_folder}/*")

                for action_index in range(len(etg_screenshots)):
                    successful_action = "NO" if str(action_index) in failing_actions else "YES"

                    etg_screenshot = f"{results_path}/etg/{test_folder}/screenshots/{test_folder}_{action_index}-*.png"
                    mate_screenshot = f"{results_path}/mate/screenshots/MATE_{test_index}_{action_index}.png"
                    comparison_screenshot = f"{screenshots_comparison_folder}/comparison_{action_index}.png"

                    output, error, return_code = run_cmd(
                        f"compare -metric AE -fuzz {fuzz_factor}% " +
                        f"{mate_screenshot} {etg_screenshot} " +
                        f"-compose Src {comparison_screenshot} 2>&1")

                    different_pixels = float(output)

                    output, error, return_code = run_cmd(
                        f"compare -metric AE -fuzz {fuzz_factor}% " +
                        f"{mate_screenshot} {home_screenshot} " +
                        f"null: 2>&1")

                    different_pixels_home = float(output)

                    if total_pixels is None:
                        # do this only the first time
                        output, error, return_code = run_cmd(
                            f"identify -format '%w %h' {comparison_screenshot} 2>&1")
                        output = output.split(" ")
                        width = float(output[0])
                        height = float(output[1])
                        total_pixels = width * height

                    difference_percentage = different_pixels / total_pixels
                    different = "YES" if difference_percentage > screenshots_pixel_percentage_threshold else "NO"

                    difference_percentage_home = different_pixels_home / total_pixels
                    home = "NO" if difference_percentage_home > screenshots_pixel_percentage_threshold else "YES"

                    line = f"{package_name},{repetition},{test_index},{action_index},"
                    line += f"{successful_action},"
                    line += f"{different_pixels:.0f},{total_pixels:.0f},{difference_percentage:.5f},{different},"
                    line += f"{different_pixels_home:.0f},{difference_percentage_home:.5f},{home}"

                    csv_lines.append(line)

    action_level_csv_path = f"{cfg.results_path}/results_action_level_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv"
    with open(action_level_csv_path, 'w') as output_file:
        output_file.write("\n".join(csv_lines))

    return action_level_csv_path


def parse_failing_actions(package_name, repetition):
    etg_log_file = f"{cfg.results_path}/{package_name}/{repetition}/etg.log"

    output, error, return_code = run_cmd(f"cat {etg_log_file} | grep TEST:")
    lines = output.strip("\n").split("\n")

    data = {}
    current_test_index = None
    failing_actions = []
    for line in lines:
        if "COVERAGE" in line:
            # we can get the test index from this line
            # save current failing actions and parse new test index
            if current_test_index is not None:
                data[current_test_index] = failing_actions

            test_name = line.split(" ")[1]
            current_test_index = test_name.split("ETGTestCase")[1]
            failing_actions = []

        elif "FAILING-CLUSTER-INDEXES" in line:
            fields = line.split(" ")
            indexes = fields[len(fields)-1].split(",")
            failing_actions.extend(indexes)

    if current_test_index is not None:
        data[current_test_index] = failing_actions

    return data
