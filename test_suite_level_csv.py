import csv
import datetime

import cfg
from command import run_cmd

column_names = [
    "Subject",
    "Repetition",

    "MATE combined coverage",
    "ETG combined coverage",
    "Combined coverage difference",

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
]

def build(test_case_level_csv_path: str):
    csv_lines = []

    # add column names
    csv_lines.append(",".join(list(map(lambda c: f"\"{c}\"", column_names))))

    with open(test_case_level_csv_path, mode='r') as test_case_level_csv_file:
        test_case_level_csv_reader = csv.DictReader(test_case_level_csv_file)
        test_case_level_csv_rows = list(test_case_level_csv_reader)

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

                line = f"{package_name},{repetition},"

                # gather MATE final combined coverage
                output, error, return_code = run_cmd(f"cat {cfg.results_path}/{package_name}/{repetition}/mate_server.log | grep \"combined coverage:\" | tail -n 1")
                fields = output.strip("\n").split(" ")
                mate_total_combined_coverage = float(fields[len(fields)-1])

                # gather ETG data
                etg_log_file = f"{cfg.results_path}/{package_name}/{repetition}/etg.log"

                output, error, return_code = run_cmd(f"cat {etg_log_file} | grep ETG-ONLY-OVERALL-COVERAGE | cut -d' ' -f 2")
                etg_only_overall_coverage = float(output.strip("\n"))

                line += f"{mate_total_combined_coverage},"  # "MATE combined coverage",
                line += f"{etg_only_overall_coverage},"  # "ETG combined coverage",
                line += f"{mate_total_combined_coverage - etg_only_overall_coverage},"  # "Combined coverage difference",

                test_cases = [row for row in test_case_level_csv_rows if
                                row["Subject"] == package_name and
                                row["Repetition"] == repetition]

                total_actions = sum(map(lambda r: int(r["Total actions"]), test_cases))
                failing_actions = sum(map(lambda r: int(r["Failing actions"]), test_cases))
                percentage_failing_actions = float(failing_actions) / float(total_actions)

                diverging_screenshots = sum(map(lambda r: int(r["Diverging screenshots"]), test_cases))
                percentage_diverging_screenshots = float(diverging_screenshots) / float(total_actions)

                total_actions_no_home = sum(map(lambda r: int(r["Total actions (no HOME)"]), test_cases))
                failing_actions_no_home = sum(map(lambda r: int(r["Failing actions (no HOME)"]), test_cases))
                percentage_failing_actions_no_home = float(failing_actions) / float(total_actions)

                diverging_screenshots_no_home = sum(map(lambda r: int(r["Diverging screenshots (no HOME)"]), test_cases))
                percentage_diverging_screenshots_no_home = float(diverging_screenshots) / float(total_actions)

                line += f"{total_actions},"  # "Total actions",
                line += f"{failing_actions},"  # "Failing actions",
                line += f"{percentage_failing_actions},"  # "Percentage failing actions",

                line += f"{diverging_screenshots},"  # "Diverging screenshots",
                line += f"{percentage_diverging_screenshots},"  # "Percentage diverging screenshots",

                line += f"{total_actions_no_home},"  # "Total actions (no HOME)",
                line += f"{failing_actions_no_home},"  # "Failing actions (no HOME)",
                line += f"{percentage_failing_actions_no_home},"  # "Percentage failing actions (no HOME)",

                line += f"{diverging_screenshots_no_home},"  # "Diverging screenshots (no HOME)",
                line += f"{percentage_diverging_screenshots_no_home}"  # "Percentage diverging screenshots (no HOME)",

                csv_lines.append(line)

    test_suite_level_csv_path = f"{cfg.results_path}/results_test_suite_level_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv"
    with open(test_suite_level_csv_path, 'w') as output_file:
        output_file.write("\n".join(csv_lines))

    return test_suite_level_csv_path
