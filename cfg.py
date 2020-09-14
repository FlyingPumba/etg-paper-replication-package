import os

from command import run_simple_cmd, run_cmd

wd = None
results_path = None
ANDROID_HOME = None
emulator_path = None
ANDROID_EMULATOR_HOME = None
ANDROID_AVD_HOME = None
android_env_variables = None
no_window = None
no_accel = None
subjects_folder = None
mate_server_folder = None
mate_client_folder = None
etg_folder = None
output_to_null = None
mate_algorithm = None
etg_pruning_algorithm = "optimistic"  # Options: optimistic, pesimistic, snapshot, no-pruning

run_only_etg = False


def setup():
    global wd
    output, error, return_code = run_cmd(f"pwd")
    wd = output.rstrip("\n")

    global results_path
    results_path = os.path.join(wd, "results")
    run_simple_cmd(f"mkdir -p {results_path}")

    global ANDROID_HOME
    ANDROID_HOME = os.path.join(wd, "android-sdk")
    os.environ["ANDROID_HOME"] = ANDROID_HOME

    global emulator_path
    emulator_path = os.path.join(ANDROID_HOME, "emulator/emulator")

    global ANDROID_EMULATOR_HOME
    ANDROID_EMULATOR_HOME = os.path.join(wd, "emulators")
    os.environ["ANDROID_EMULATOR_HOME"] = ANDROID_EMULATOR_HOME

    global ANDROID_AVD_HOME
    ANDROID_AVD_HOME = os.path.join(ANDROID_EMULATOR_HOME, "avd")
    os.environ["ANDROID_AVD_HOME"] = ANDROID_AVD_HOME

    global android_env_variables
    android_env_variables = f"ANDROID_HOME={ANDROID_HOME} ANDROID_AVD_HOME={ANDROID_AVD_HOME} ANDROID_EMULATOR_HOME={ANDROID_EMULATOR_HOME} "

    global no_window
    no_window = True

    global no_accel
    no_accel = False

    global subjects_folder
    subjects_folder = "subjects"

    global mate_server_folder
    mate_server_folder = os.path.join(wd, "etg-mate-server")

    global mate_client_folder
    mate_client_folder = os.path.join(wd, "etg-mate")

    global etg_folder
    etg_folder = os.path.join(wd, "etg")

    global output_to_null
    output_to_null = "> /dev/null 2>&1"

    global mate_algorithm
    # mate_algorithm = "RandomTestSuiteExploration"
    mate_algorithm = "RandomExploration" # This is the one used in the ICTSS paper
    # mate_algorithm = "RandomWalkActivityCoverage"
    # mate_algorithm = "RandomWalk"  # this one has statement coverage in the test cases json
