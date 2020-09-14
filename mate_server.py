import os
import sys

from command import run_simple_cmd, run_cmd
from etg_config import ETGConfig
import emulators
import cfg


def prepare_mate_server(results_path):
    print("Prepare MATE server")
    run_simple_cmd(f"{cfg.mate_server_folder}/gradlew -p {cfg.mate_server_folder} fatJar > {results_path}/mate_server.log 2>&1")
    output, error, return_code = run_cmd(f"cat {results_path}/mate_server.log | grep 'BUILD FAILED'")
    if 'BUILD FAILED' in output:
        print(f"An error occurred while preparing MATE server:\n{output}\n{error}")
        sys.exit()
    run_simple_cmd("pkill -f mate-server")
    run_simple_cmd(f"rm -r {cfg.mate_server_folder}/*.apk {cfg.mate_server_folder}/*.src "
                   f"{cfg.mate_server_folder}/*.coverage {cfg.mate_server_folder}/*.coverage.empty")
    run_simple_cmd("sleep 5")
    mate_exploration_timeout = 60  # timeout for MATE exploration in minutes
    run_simple_cmd(
        f"cd {cfg.mate_server_folder}; java -jar build/libs/mate-server-all-1.0-SNAPSHOT.jar {mate_exploration_timeout} >> {results_path}/mate_server.log 2>&1 &")


def prepare_coverage_files(package_name: str, etg_config: ETGConfig):
    print("Preparing coverage files for MATE server")
    run_simple_cmd(f"{cfg.android_env_variables} $ANDROID_HOME/platform-tools/adb root")

    package_name_path = "/".join(package_name.split("."))

    # prepare <package_name>.apk file
    apk_path = emulators.get_apk_path(package_name)
    run_simple_cmd(f"cp {apk_path} {cfg.mate_server_folder}/{etg_config.compiled_package_name()}.apk")

    # prepare <package_name>.coverage.empy file
    emulators.launch_main_activity(etg_config)
    run_simple_cmd("sleep 30")

    output, errors, result_code = run_cmd( f"{cfg.android_env_variables} $ANDROID_HOME/platform-tools/adb shell "
            f"am broadcast -a evolutiz.emma.COLLECT_COVERAGE "
            f"-n {etg_config.compiled_package_name()}/{etg_config.package_name()}.EmmaInstrument.CollectCoverageReceiver")
    run_simple_cmd("sleep 30")
    output, error, return_code = run_cmd(f"{cfg.android_env_variables} $ANDROID_HOME/platform-tools/adb pull "
                   f"/data/user/0/{etg_config.compiled_package_name()}/files/coverage.ec "
                   f"{cfg.mate_server_folder}/{etg_config.compiled_package_name()}.coverage.empty")

    if 'error' in output:
        raise Exception(f"Unable to fetch empty coverage from app {package_name}")

    # prepare <package_name>.src folder
    mate_server_src_folder_path = f"{cfg.mate_server_folder}/{etg_config.compiled_package_name()}.src/"
    run_simple_cmd(f"mkdir -p {mate_server_src_folder_path}")

    output, error, return_code = run_cmd(f"find {cfg.subjects_folder}/{package_name}/ -name \"*.class\" -type f")
    class_files = list(filter(lambda f: f != "", output.split("\n")))

    build_variant = "debug"
    build_variant_path = build_variant

    product_flavors = etg_config.product_flavors()
    if len(product_flavors) > 0:
        product_flavors_combined = ''
        product_flavors_combined_path = ''
        for index, flavor in enumerate(product_flavors):
            if index == 0:
                product_flavors_combined += flavor.lower()
            else:
                product_flavors_combined += flavor.capitalize()

            product_flavors_combined_path += f"/{flavor.lower()}"

        build_variant = product_flavors_combined + etg_config.build_type()[0].capitalize() + etg_config.build_type()[1:]
        build_variant_path = product_flavors_combined_path + f"/{etg_config.build_type()}/"

        if package_name_path.endswith(product_flavors_combined):
            package_name_path = package_name_path.split("/" + product_flavors_combined)[0]

    class_files = list(filter(lambda f:
                              (build_variant in f or build_variant_path in f)
                              and "AndroidTest" not in f
                              and "androidTest" not in f
                              and "UnitTest" not in f
                              and "R$" not in f
                              and "R.class" not in f
                              and "BuildConfig.class" not in f
                              and "/EmmaInstrument/" not in f
                              and "/jacoco_instrumented_classes/" not in f
                              and "/jacoco/" not in f
                              and "/transforms/" not in f
                              and "/kapt3/" not in f,
                              class_files))

    mate_server_classes_folder_path = f"{mate_server_src_folder_path}classes/"
    run_simple_cmd(f"mkdir -p {mate_server_classes_folder_path}")

    # Proceed to find the root folder where package name start for each class file. For example:
    # 'subjects/com.a42crash.iarcuschin.a42crash/app/build/tmp/kotlin-classes/debug/com/a42crash/iarcuschin/a42crash/MainActivity.class'
    # -> We should copy from the /debug/ folder onwards
    # 'subjects/com.a42crash.iarcuschin.a42crash/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes/com/a42crash/iarcuschin/a42crash/MainActivity_ViewBinding.class'
    # -> We should copy from the /classes/ folder onwards

    class_folders = []
    for class_file in class_files:
        if any(class_file.startswith(folder) for folder in class_folders):
            continue

        class_file_folder = os.path.dirname(class_file)
        while not class_file_folder.endswith(cfg.subjects_folder):
            if class_file_folder.endswith(package_name_path):
                class_folder: str = class_file_folder.split(package_name_path)[0]

                if class_folder not in class_folders:
                    class_folders.append(class_folder)

                break
            else:
                class_file_folder = os.path.dirname(class_file_folder)

    # copy class folders with their directory structure
    run_simple_cmd(f"mkdir -p {mate_server_classes_folder_path}/{package_name_path}")
    for class_folder in class_folders:
        rsync_cmd = f"rsync -a --prune-empty-dirs --exclude=\"*EmmaInstrument*/\" --exclude=\"*AndroidTest*/\" " \
                f"--exclude=\"*UnitTest*/\" --exclude=\"*kapt3*/\" --exclude=\"*jacoco_instrumented_classes*/\" " \
                f"--exclude=\"*jacoco*/\" --exclude=\"*androidTest*/\" --exclude=\"*transforms*/\" " \
                f"--exclude=\"R\$*.class\" --exclude=\"BuildConfig.class\" --exclude=\"R.class\" " \
                f"--include=\"*.class\" --include=\"*/\" --exclude=\"*\" " \
                f"{class_folder}/{package_name_path}/ {mate_server_classes_folder_path}/{package_name_path}"
        run_simple_cmd(rsync_cmd)

    # Find and copy source root folder
    app_folder = os.path.dirname(class_folders[0])
    while True:
        if 'src' in os.listdir(app_folder):
            source_root = f"{app_folder}/src"
            break
        else:
            app_folder = os.path.dirname(app_folder)
            if app_folder.endswith(f"{cfg.subjects_folder}/{package_name}"):
                raise Exception(f"Unable to find source root folder for package name {package_name}")

    run_simple_cmd(f"cp -r  {source_root}/main/java {mate_server_src_folder_path}")

    if 'kotlin' in os.listdir(f"{source_root}/main/"):
        run_simple_cmd(f"cp -r  {source_root}/main/kotlin {mate_server_src_folder_path}")
