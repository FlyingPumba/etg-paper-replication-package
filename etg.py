import datetime
import os
from pathlib import Path

import cfg
from command import run_simple_cmd, run_cmd
from etg_config import ETGConfig
import emulators
import mate_client
import mate_server


def process_package_name(package_name: str, etg_config: ETGConfig, etg_config_file: str, repetition: int, results_path: str):
    etg_log_file = os.path.join(results_path, "etg.log")
    mate_screenshots_folder = os.path.join(results_path, "mate", "screenshots")
    run_simple_cmd(f"mkdir -p {mate_screenshots_folder}")

    if not cfg.run_only_etg:
        # delete json output file
        run_simple_cmd(f"rm {etg_config.json_path()}")

        emulators.build_and_install_app(package_name, etg_config)

        mate_server.prepare_coverage_files(package_name, etg_config)

        emulators.launch_main_activity(etg_config)

        mate_client.run_mate_client(etg_config, results_path)

        output, error, return_code = run_cmd(f"cat {etg_config.json_path()}")
        if output == "[]":
            raise Exception(f"MATE client for package {package_name} generated an empty JSON.")

        # copy JSON output to results folder
        json_file_path = f"{results_path}/{package_name}_{repetition}_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.json"
        run_simple_cmd(f"cp {etg_config.json_path()} {json_file_path}")

        mate_coverage, error, return_code = run_cmd(f"jq . {json_file_path} | grep \"coverage\\\"\" | cut -d' ' -f6 | cut -d',' -f1")
        mate_coverage = mate_coverage.strip("\n")
        run_simple_cmd(f"echo \"{mate_coverage}\" >> {results_path}/mate_coverage.txt")

        # move screenshots to results folder
        run_simple_cmd(f"mv {cfg.mate_server_folder}/*.png {mate_screenshots_folder}/")
    else:
        # copy existing json file
        run_simple_cmd(f"cp {results_path}/*.json {etg_config.json_path()}")

    # kill and re-setup emulator in case MATE Client didn't stop after timeout
    emulators.fire_emulators()
    emulators.build_and_install_app(package_name, etg_config)

    print("Running ETG")
    run_simple_cmd(f"{cfg.android_env_variables} {cfg.etg_folder}/gradlew -p {cfg.etg_folder} build > {etg_log_file} 2>&1")
    run_simple_cmd(
        f"{cfg.android_env_variables} java -jar {cfg.etg_folder}/build/libs/etg-1.0-SNAPSHOT.jar " +
        f"-p {cfg.etg_pruning_algorithm} {etg_config_file} {results_path} >> {etg_log_file} 2>&1")

    output, error, return_code = run_cmd(f"cat {etg_log_file}")
    if "BUILD FAILED" in output:
        raise Exception(f"There was a problem building one of the Espresso tests for package {package_name}.")
    elif "INSTRUMENTATION_CODE: -1" in output:
        raise Exception(f"There was a problem running one of the Espresso tests for package {package_name}.")
    elif "java.lang.Exception" in output:
        raise Exception(f"There was an exception running ETG for package {package_name}.")
    elif "ETG finished" not in output:
        raise Exception(f"ETG did not finish successfully for package {package_name}.")

    etg_coverage, error, return_code = run_cmd(f"cat {etg_log_file} | grep \" COVERAGE:\" | cut -d':' -f 3")
    etg_coverage = etg_coverage.strip("\n")
    run_simple_cmd(f"echo \"{etg_coverage}\" >> {results_path}/etg_coverage.txt")
