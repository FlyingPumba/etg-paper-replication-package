# ETG: Espresso Test Generator

This repository contains the empirical study of the paper **"ETG: Creating ESPRESSO tests from sequences of widget actions -- challenges and limitations"**.
To maintain this repository as lightweight as possible, the [results used in the paper are available for download from Google Drive](https://drive.google.com/file/d/1evX2q_A58DbMcrvLbE98DUM6lOHR7u4K/view).

We provide below instructions to setup and run the experiments.
If you wish to just download the ETG tool, you can find it in [its own repository](https://github.com/FlyingPumba/etg).

## Setup instructions

For running the experiments we recommend using a machine with at least 8GB of RAM and 4 CPUs.
You will also need 25GB of free disk space to download all the subjects, Android SDK and emulator.
These instructions assume you have Ubuntu 20.04 as Operating System with `Python 3` installed.

0. Download and cd into this repository 
```bash
git clone git://github.com/FlyingPumba/etg-paper-replication-package.git && cd etg-paper-replication-package
```
1. Run `./setup_experiments_0.sh` script to install various utilities. If you find a `Unable to locate packge` error, make sure that you have enabled the main Ubuntu repositories by running `sudo add-apt-repository main`. You may need to restart the computer after this step if installing OpenGLES.
2. Run `./setup_experiments_1.sh` script to install Android SDK locally.You will also need to add the following lines at the end of your `~/.bashrc` file, replacing `DOWNLOAD_PATH` with the absolute path were this repo was downloaded (e.g., `/home/user/etg-paper-replication-package`):
```bash
export ANDROID_HOME='DOWNLOAD_PATH/android-sdk'
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/tools/bin:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools
```
3. Run `./setup_experiments_2.sh` script to install an Android emulator.
4. Run `./setup_experiments_3.sh` script to download the subjects for the experimentation along with ETG and MATE's extension. It also downloads the Python dependencies in a isolated environment using `virtualenv` command.

## Run instructions

- Activate the new `PATH` variable added to the `~/.bashrc` file.
```bash
source ~/.bashrc
```

- To make sure that you have set the environment variables correctly, run `type adb` and check that it yields a valid path (e.g., `/home/user/etg-paper-replication-package/android-sdk/platform-tools/adb`).

- Activate the isolated `Python` environment.
```bash
source .env/bin/activate
```
- Execute the runner
```bash
./run_experiments.py
```

## Experiment configuration

There are several parameters that can be tweaked:

- Number of repetitions to run for each subject: modify the [`repetitions` variable in `run_experiments.py` file.](https://github.com/FlyingPumba/etg-paper-replication-package/blob/master/run_experiments.py#L17)

- Repetitions offset: modify the [`repetitions_init` variable in `run_experiments.py` file.](https://github.com/FlyingPumba/etg-paper-replication-package/blob/master/run_experiments.py#L16)

- MATE's time budget for exploration: modify the [`mate_exploration_timeout` variable in `mate_server.py` file.](https://github.com/FlyingPumba/etg-paper-replication-package/blob/master/mate_server.py#L21)

- MATE's exploration algorithm: modify the [`mate_algorithm` variable in `cfg.py` file](https://github.com/FlyingPumba/etg-paper-replication-package/blob/master/cfg.py#L75)

- Turn on or off emulator's window (default is off): modify the [`no_window` variable in `cfg.py` file](https://github.com/FlyingPumba/etg-paper-replication-package/blob/master/cfg.py#L53)

- Further configurations can be found in [`cfg.py` file]((https://github.com/FlyingPumba/etg-paper-replication-package/blob/master/cfg.py)). Most of them are just path folders. They shouldn't need modification if the setup scripts are being used.

## Tools' repositories

- [ETG repository](https://github.com/FlyingPumba/etg)

- [MATE's client extension repository](https://github.com/FlyingPumba/etg-mate)

- [MATE's server extension repository](https://github.com/FlyingPumba/etg-mate-server)

## Subjects' repositories

| Name | Original repository | Forked repository |
| ------------- | :-------------: | :-------------: |
| PoetAssistant | [link](https://github.com/caarmen/poet-assistant) | [link](https://github.com/FlyingPumba/poet-assistant) |
| Equate        | [link](https://github.com/EvanRespaut/Equate) | [link](https://github.com/FlyingPumba/Equate) |
| OneTimePad    | [link](https://github.com/kckrinke/onetimepad) | [link](https://github.com/FlyingPumba/onetimepad) |
| Orgzly        | [link](https://github.com/orgzly/orgzly-android) | [link](https://github.com/FlyingPumba/orgzly-android) |
| MicroPinner   | [link](https://github.com/dotWee/MicroPinner) | [link](https://github.com/FlyingPumba/MicroPinner) |
| OCReader      | [link](https://github.com/schaal/ocreader) | [link](https://github.com/FlyingPumba/ocreader) |
| HomeAssistant | [link](https://github.com/Maxr1998/home-assistant-Android) | [link](https://github.com/FlyingPumba/home-assistant-Android) |
| OmniNotes     | [link](https://github.com/federicoiosue/Omni-Notes) | [link](https://github.com/FlyingPumba/Omni-Notes) |
| Kontalk       | [link](https://github.com/kontalk/androidclient) | [link](https://github.com/FlyingPumba/androidclient) |
| KolabNotes    | [link](https://github.com/konradrenner/kolabnotes-android) | [link](https://github.com/FlyingPumba/kolabnotes-android) |
| ShoppingList  | [link](https://github.com/openintents/shoppinglist) | [link](https://github.com/FlyingPumba/shoppinglist) |
| MyExpenses    | [link](https://github.com/mtotschnig/MyExpenses) | [link](https://github.com/FlyingPumba/MyExpenses) |
