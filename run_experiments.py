#!.env/bin/python
import os

import action_level_csv
import test_case_level_csv
import test_suite_level_csv
from command import run_cmd, run_simple_cmd
from pathlib import Path
import emulators
import etg
import cfg
import mate_client
import mate_server
from etg_config import ETGConfig

repetitions_init = 0
repetitions = 1

# None to disable, otherwise a list of strings. Example: ["com.onest8.onetimepad"]
package_names_white_list = [
    "ca.rmen.android.poetassistant",
    "com.llamacorp.equate",
    "com.onest8.onetimepad",
    "com.orgzly",
    "de.dotwee.micropinner",
    "email.schaal.ocreader",
    "io.homeassistant.android",
    "it.feio.android.omninotes.foss",
    "org.kontalk",
    "org.kore.kolabnotes.android",
    "org.openintents.shopping",
    "org.totschnig.myexpenses",
]
package_names_black_list = None  # None to disable, otherwise a list of strings. Example: ["com.onest8.onetimepad"]

if __name__ == "__main__":
    cfg.setup()

    output, error, return_code = run_cmd(f"ls {cfg.subjects_folder}")
    package_names = output.split("\n")

    for repetition in range(repetitions_init, repetitions):
        for package_name in package_names:
            if package_name == "":
                continue

            if package_names_white_list is not None:
                if package_name not in package_names_white_list:
                   continue

            if package_names_black_list is not None:
                if package_name in package_names_black_list:
                    continue

            etg_config_file = os.path.join(cfg.subjects_folder, package_name, "etg.config")

            print(f"\n\n #### Processing package {package_name}\n\n")

            if Path(etg_config_file).exists():
                print(f"ETG config file: {etg_config_file}")
            else:
                print(f"ETG config file does NOT exists: {etg_config_file}")
                continue

            etg_config = ETGConfig(etg_config_file)

            results_path = os.path.join(cfg.results_path, etg_config.compiled_package_name(), str(repetition))

            if not cfg.run_only_etg:
                # create results folder for this app
                run_simple_cmd(f"rm -r {results_path}")
                run_simple_cmd(f"mkdir -p {results_path}")

                emulators.fire_emulators()

                mate_server.prepare_mate_server(results_path)

                mate_client.prepare_mate_client(results_path)

            etg.process_package_name(package_name, etg_config, etg_config_file, repetition, results_path)

            run_simple_cmd("sleep 10")

    print(f"\n\n #### Building CSV files\n\n")
    #
    action_level_csv_path = action_level_csv.build()
    test_case_level_csv_path = test_case_level_csv.build(action_level_csv_path)
    test_suite_level_csv_path = test_suite_level_csv.build(test_case_level_csv_path)
