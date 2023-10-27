# Hotspot-Detection

Hotspot-Detection is an open-source tool that helps software developers to detect hotspots in their programs. This allows to focus optimization efforts to where it really matters.

Code regions (loops and functions) are categorized into three classes (HOT, WARM, COLD) according to the following criteria:

A) the code region contributes a lot to the total runtime of the program. \
B) the runtime of the code region increases a lot when using different program parameters.

- HOT code regions fulfill both _(A and B)_
- WARM code regions fulfill only one _(A xor B)_
- COLD code regions fulfill neither  _(not(A or B))_


## Installation

Install the requirements:

```
sudo apt install git build-essential cmake libclang-11-dev clang-11 llvm-11 python3
```

Install the Hotspot-Detection:

```
git clone git@github.com:discopop-project/Hotspot-Detection.git
cd Hotspot-Detection
mkdir build
cd build
cmake ..
make
```


## Usage

The Hotspot-Detection is built on the llvm project and has two core components:
- The **llvm optimizer pass** modifies the program during compilation. With these modifications we automatically monitor how much time your program spends in any code region.
- A **python tool** analyzes the measured runtimes of the code regions and reports hotspots.

It is possible to manually use these components on (almost) any project. However we also provide a script that wraps the CMake build process to automatically apply the llvm optimizer pass for you. Simply perform the following steps to analyze any project that is built using CMake.

### 1) Build your project and apply the hotspot-detection instrumentation

```
cd <your_project_directory>
mkdir build
cd build
<HOTSPOT_DETECTION_BUILD>/scripts/CMAKE_wrapper.sh ..
make
```

Note that it is possible to add your own custom flags for the cmake build.

### 2) Run the instrumented program

Run your program multiple times with varying parameters.

```
./<your_program_name> <your_program arguments_1>
./<your_program_name> <your_program arguments_2>
./<your_program_name> <your_program arguments_3>
# ...
```

### 3) Analyze the results

Change your working directory so you are inside the `.discopop` directory. By default it is located inside the build directory.

```
hotspot_analyzer
```

You can now find the analysis results inside `.discopop/hotspot_detection`.
