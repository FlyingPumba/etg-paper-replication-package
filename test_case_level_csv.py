import csv
import datetime

import cfg
from command import run_cmd

column_names = [
    "Subject",
    "Repetition",
    "Test index",

    "MATE coverage",
    "ETG coverage",
    "Coverage difference",

    "Total actions",
    "Failing actions",
    "Percentage failing actions",

    "Diverging screenshots",
    "Percentage diverging screenshots",

    "Total actions (no HOME)",
    "Failing actions (no HOME)",
    "Percentage failing actions (no HOME)",

    "Diverging screenshots (no HOME)",
    "Percentage diverging screenshots (no HOME)",

    "Base test suite overall coverage",
    "Overall coverage including ETG test",
    "Overall coverage difference increase",
]

def build(action_level_csv_path: str):
    csv_lines = []

    # add column names
    csv_lines.append(",".join(list(map(lambda c: f"\"{c}\"", column_names))))

    with open(action_level_csv_path, mode='r') as action_level_csv_file:
        action_level_csv_reader = csv.DictReader(action_level_csv_file)
        action_level_csv_rows = list(action_level_csv_reader)

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

                # gather MATE data
                output, error, return_code = run_cmd(f"cat {cfg.results_path}/{package_name}/{repetition}/mate_coverage.txt")
                mate_coverage = list(map(lambda c: float(c), output.strip("\n").split("\n")))

                # gather ETG data
                etg_log_file = f"{cfg.results_path}/{package_name}/{repetition}/etg.log"

                output, error, return_code = run_cmd(f"cat {etg_log_file} | grep BASE-OVERALL-COVERAGE | cut -d' ' -f 2")
                base_overall_coverage = float(output.strip("\n"))

                output, error, return_code = run_cmd(f"cat {etg_log_file} | grep \" COVERAGE\" | cut -d' ' -f 4")
                etg_coverage = list(map(lambda c: float(c), output.strip("\n").split("\n")))

                output, error, return_code = run_cmd(f"cat {etg_log_file} | grep OVERALL-COVERAGE-INCLUDING-TEST | cut -d' ' -f 4")
                etg_overall_coverage_including_test = list(map(lambda c: float(c), output.strip("\n").split("\n")))

                for test_index in range(0, len(mate_coverage)):

                    line = f"{package_name},{repetition},{test_index},"
                    line += f"{mate_coverage[test_index]:.5f},{etg_coverage[test_index]:.5f},{mate_coverage[test_index] - etg_coverage[test_index]:.5f},"

                    test_actions = [row for row in action_level_csv_rows if
                                   row["Subject"] == package_name and
                                   row["Repetition"] == repetition and
                                   row["Test index"] == str(test_index)]

                    total_actions = len(test_actions)
                    failing_actions = len([row for row in test_actions if row["Successful in ETG?"] == "NO"])
                    percentage_failing_actions = float(failing_actions)/float(total_actions)

                    diverging_screenshots = len([row for row in test_actions if row["Different screenshots?"] == "YES"])
                    percentage_diverging_screenshots = float(diverging_screenshots) / float(total_actions)

                    test_actions_no_home = [row for row in action_level_csv_rows if
                                            row["Subject"] == package_name and
                                            row["Repetition"] == repetition and
                                            row["Test index"] == str(test_index) and
                                            row["Home?"] == "NO"]

                    total_actions_no_home = len(test_actions_no_home)
                    failing_actions_no_home = len([row for row in test_actions_no_home if row["Successful in ETG?"] == "NO"])
                    percentage_failing_actions_no_home = float(failing_actions_no_home) / float(total_actions_no_home)

                    diverging_screenshots_no_home = len([row for row in test_actions if row["Different screenshots?"] == "YES"])
                    percentage_diverging_screenshots_no_home = float(diverging_screenshots_no_home) / float(total_actions)

                    overall_coverage_including_test = etg_overall_coverage_including_test[test_index]
                    overall_coverage_difference_increase = overall_coverage_including_test - base_overall_coverage

                    line += f"{total_actions},"  # "Total actions",
                    line += f"{failing_actions},"  # "Failing actions",
                    line += f"{percentage_failing_actions},"  # "Percentage failing actions",

                    line += f"{diverging_screenshots},"  # "Diverging screenshots",
                    line += f"{percentage_diverging_screenshots},"  # "Percentage diverging screenshots",

                    line += f"{total_actions_no_home},"  # "Total actions (no HOME)",
                    line += f"{failing_actions_no_home},"  # "Failing actions (no HOME)",
                    line += f"{percentage_failing_actions_no_home},"  # "Percentage failing actions (no HOME)",

                    line += f"{diverging_screenshots_no_home},"  # "Diverging screenshots (no HOME)",
                    line += f"{percentage_diverging_screenshots_no_home},"  # "Percentage diverging screenshots (no HOME)",

                    line += f"{base_overall_coverage},"  # "Base test suite overall coverage",
                    line += f"{overall_coverage_including_test},"  # "Overall coverage including ETG test",
                    line += f"{overall_coverage_difference_increase}"  # "Overall coverage difference increase",

                    csv_lines.append(line)

    test_case_level_csv_path = f"{cfg.results_path}/results_test_case_level_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv"
    with open(test_case_level_csv_path, 'w') as output_file:
        output_file.write("\n".join(csv_lines))

    return test_case_level_csv_path
