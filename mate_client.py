import sys

from command import run_simple_cmd, run_cmd
from etg_config import ETGConfig
import cfg

def prepare_mate_client(results_path):
    print("Prepare MATE client")
    run_simple_cmd(
        f"{cfg.android_env_variables} {cfg.mate_client_folder}/gradlew -p {cfg.mate_client_folder} installDebug > {results_path}/mate_client.log 2>&1")
    run_simple_cmd(
        f"{cfg.android_env_variables} {cfg.mate_client_folder}/gradlew -p {cfg.mate_client_folder} installDebugAndroidTest >> {results_path}/mate_client.log 2>&1")
    output, error, return_code = run_cmd(f"cat {results_path}/mate_client.log | grep 'BUILD FAILED'")
    if 'BUILD FAILED' in output:
        print(f"An error occurred while preparing MATE client:\n{output}\n{error}")
        sys.exit()


def run_mate_client(etg_config: ETGConfig, results_path: str) -> bool:
    print("Running MATE client")
    output, error, return_code = run_cmd(
        f"$ANDROID_HOME/platform-tools/adb shell am instrument -w -r -e debug false -e class org.mate.ExecuteMATE{cfg.mate_algorithm} "
        f"org.mate.test/androidx.test.runner.AndroidJUnitRunner",
        timeout=8 * 60 * 60,
        discard_output=False,
        cwd=cfg.wd,
        env={
            "ANDROID_HOME": cfg.ANDROID_HOME,
            "ANDROID_AVD_HOME": cfg.ANDROID_AVD_HOME,
            "ANDROID_EMULATOR_HOME": cfg.ANDROID_EMULATOR_HOME,
        }
    )

    with open(f"{results_path}/mate_client.log", "a") as log_file:
        # Append output at the end of file
        log_file.write(output)

    dump_adb_logcat(results_path)

    if "OK (1 test)" not in output:
        print(
            f"An error occurred while running MATE client for package {etg_config.package_name()}:\n{output}\n{error}")
        return False
    return True


def dump_adb_logcat(results_path):
    # MATE uses a lot of different tags: "apptest", "acc", "vinDebug", plus a lot of other custom ones for particular
    # classes. We are going to gather only the 3 mentioned.
    logcatCmd = f"$ANDROID_HOME/platform-tools/adb logcat -d -s acc:* apptest:* vinDebug:* > {results_path}/mate_client_logcat.log 2>&1"
    run_simple_cmd(logcatCmd)
