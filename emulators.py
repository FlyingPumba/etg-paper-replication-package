import os

import cfg
from command import run_simple_cmd, run_cmd
from etg_config import ETGConfig


def kill_running_emulators():
    run_simple_cmd(
        f"{cfg.android_env_variables} $ANDROID_HOME/platform-tools/adb devices | grep emulator | cut -f1 | while read line; do $ANDROID_HOME/platform-tools/adb -s $line emu kill {cfg.output_to_null}; done")


def fire_emulators():
    print("Fire up emulator")

    while True:
        kill_running_emulators()

        emulator_cmd = f"{cfg.android_env_variables} {cfg.emulator_path} {'-no-window' if cfg.no_window else ''} -no-snapshot -no-boot-anim -writable-system -wipe-data {'-no-accel' if cfg.no_accel else ''} -avd Nexus_5X_API_28_0 {cfg.output_to_null} &"
        run_simple_cmd(emulator_cmd)
        run_simple_cmd("sleep 300")

        # Check if we have a system.ui dialog that says "System UI not responding". E.g.,
        # mCurrentFocus=Window{45b1ddc u0 Application Not Responding: com.android.systemui}
        output, error, return_code = run_cmd("$ANDROID_HOME/platform-tools/adb shell dumpsys window windows | grep -i mCurrentFocus")
        if not ("Not Responding" in output and "com.android.systemui" in output):
            break


def grant_permissions(package_name: str, etg_config: ETGConfig):
    output, error, return_code = run_cmd("$ANDROID_HOME/platform-tools/adb shell pm list permissions -d -g | grep permission: | cut -d':' -f2")
    permissions = filter(lambda p: p != "", output.split('\n'))
    for permission in permissions:
        run_simple_cmd(f"$ANDROID_HOME/platform-tools/adb shell pm grant {etg_config.compiled_package_name()} {permission} >/dev/null 2>&1")


def build_and_install_app(package_name: str, etg_config: ETGConfig) -> bool:
    print("Building and installing app")
    run_simple_cmd(f"chmod +x {cfg.subjects_folder}/{package_name}/gradlew {cfg.output_to_null}")

    output, error, return_code = run_cmd(
        f"{cfg.subjects_folder}/{package_name}/gradlew -p {cfg.subjects_folder}/{package_name} "
        f"install{''.join(map(lambda f: f.capitalize(), etg_config.product_flavors()))}{etg_config.build_type().capitalize()}",
        timeout=20 * 60,
        discard_output=False,
        cwd=cfg.wd,
        env={
            "ANDROID_HOME": cfg.ANDROID_HOME,
            "ANDROID_AVD_HOME": cfg.ANDROID_AVD_HOME,
            "ANDROID_EMULATOR_HOME": cfg.ANDROID_EMULATOR_HOME,
        }
    )

    if "BUILD SUCCESSFUL" not in output:
        print(f"An error occurred while building {package_name}:\n{output}\n{error}")
        return False

    grant_permissions(package_name, etg_config)

    return True


def launch_main_activity(etg_config: ETGConfig) -> bool:
    # open app without known Main activity name
    print("Opening Launcher activity")
    output, error, return_code = run_cmd(
        f"{cfg.android_env_variables} $ANDROID_HOME/platform-tools/adb shell monkey -p {etg_config.compiled_package_name()} -c android.intent.category.LAUNCHER 1")
    if "No activities found to run, monkey aborted" in output:
        print(
            f"An error occurred while opening launching app with Monkey for package {etg_config.compiled_package_name()}:\n{output}\n{error}")
        return False
    return True


def stop_main_activity(etg_config: ETGConfig) -> bool:
    # open app without known Main activity name
    print("Opening Launcher activity")
    output, error, return_code = run_cmd(
        f"{cfg.android_env_variables} $ANDROID_HOME/platform-tools/adb shell am force-stop {etg_config.compiled_package_name()}")
    return True


def get_apk_path(package_name) -> str:
    subject_folder = f"{cfg.subjects_folder}/{package_name}/"
    # now find its name
    output, errors, result_code = run_cmd(f"find {subject_folder} -name *.apk | grep -v androidTest | grep -v unaligned")
    apk_paths = []
    for file_path in output.split("\n"):
        if file_path != "":
            apk_paths.append(file_path)

    if len(apk_paths) == 0:
        raise Exception(f"No APKs found inside folder {subject_folder} after build.")

    if len(apk_paths) > 1:
        # try to filter APKs based on ETG.config file (might not be present)
        etg_config_path = f"{subject_folder}/etg.config"
        if os.path.isfile(etg_config_path):
            etg_config = ETGConfig(etg_config_path)

            # try to filter by build type
            build_type = etg_config.build_type()
            apk_paths = list(filter(lambda path: f"/{build_type}/" in path, apk_paths))

            # try to filter by product flavors
            product_flavors = etg_config.product_flavors()
            if len(product_flavors) > 0:
                product_flavors_combined = ''
                for index, flavor in enumerate(product_flavors):
                    if index == 0:
                        product_flavors_combined += flavor.lower()
                    else:
                        product_flavors_combined += flavor.capitalize()

                apk_paths = list(filter(lambda path: f"/{product_flavors_combined}/" in path, apk_paths))

                if len(apk_paths) == 0:
                    raise Exception(f"Evolutiz was unable to determine which APK inside folder "
                                    f"{subject_folder} should it use, since neither of them satisfy the "
                                    f"combined product flavor provided: {product_flavors_combined} in the ETG config "
                                    f"file")
        else:
            # TODO: provide more info about ETG config files
            raise Exception(f"There are several APKs found inside folder {subject_folder} after "
                            f"build. Evolutiz was unable to determine which one should it use. "
                            f"You can help it by providing an ETG config file at the root of the app's folder.")

    return apk_paths[0].replace(" ", "\\ ")  # escape white spaces
