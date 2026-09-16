---
tags:
  - Project
Finish: false
date: 2026-09-12
---

# Robotic Arm

[简体中文](readme-cn.md) | **English**

A robotic arm project workspace containing mechanical models and 3D printing resources, an STM32F103 firmware project, and D-H and URDF reference files.

Last updated: 2026-09-13

## Project Structure

| Directory or file | Purpose | Main entry points |
| --- | --- | --- |
| `1. Model/` | STEP models, 3D printing files, and assembly instructions | [ZERO_ARM.STEP](<1. Model/STEP/ZERO_ARM.STEP>), [3d_printing_all.3mf](<1. Model/3d_printing_all.3mf>), [Assembly guide](<1. Model/installation_guide.md>) |
| `2. Software/` | STM32CubeIDE firmware project, including HAL and FreeRTOS | [robot_f103.ioc](<2. Software/robot_f103.ioc>), [main.c](<2. Software/Core/Src/main.c>), [freertos.c](<2. Software/Core/Src/freertos.c>) |
| `3. Simulink/` | MATLAB initialization script, D-H table, and URDF resources | [robot_run.m](<3. Simulink/robot_run.m>), [D-H.md](<3. Simulink/D-H.md>) |
| `3. Simulink/UDRT/` | ROS 2 robot description package named `zero_arm_description` | [URDF](<3. Simulink/UDRT/urdf/zero_arm_description.urdf>), [Display launch file](<3. Simulink/UDRT/launch/display.launch.py>), [package.xml](<3. Simulink/UDRT/package.xml>) |
| `AGENTS.md` | Shared project collaboration, verification, and README maintenance rules; also the Codex project instruction entry point | [Read the rules](AGENTS.md) |

## Getting Started

### Mechanical Model

Use CAD software that supports STEP to inspect `1. Model/STEP/`, and a slicer that supports 3MF to open the printing file. Check the assembly guide against the physical parts before assembly.

### Firmware

Import the existing project configuration in `2. Software/` into STM32CubeIDE. Start with `robot_f103.ioc`, `Core/Src/main.c`, and `Core/Src/freertos.c`.

The current `.ioc` specifies **STM32F103VET6** and **STM32CubeIDE** as the target toolchain. `main.c` initializes GPIO, DMA, CAN, USART1, USART3, and the RTOS. The default task toggles the red LED every 500 ms. Firmware execution and robotic arm control capabilities require separate verification.

### MATLAB and Robot Description

In MATLAB, set the current folder to this project's `3. Simulink/` directory, then run `robot_run.m`. The script clears the workspace and Command Window, and adds the current directory and its subdirectories to the search path. Save any workspace data you need before running it.

The current script does not load a model or call `sim`. No `.slx` or `.mdl` files have been found in this project. `D-H.md` provides the kinematic parameter table; connecting these parameters to an actual model and validating them still requires separate work.

`UDRT/` is a ROS 2 description package. Its `package.xml` declares dependencies including `ament_cmake`, `robot_state_publisher`, `joint_state_publisher_gui`, and `rviz2`. `display.launch.py` provides entry points for robot state publishing, a joint slider interface, and RViz visualization. Prepare a compatible ROS 2 environment and build the package before use.

## Status and Next Steps

- **Checked:** Directory structure, main entry points, F103 project configuration, the default task, and the MATLAB script contents.
- **Missing:** The assembly guide references `4. Other/Images/`, which is absent from this project, so its illustrations are currently unavailable.
- **To add:** An actual model and its execution entry point are needed for Simulink simulation.
- **Not yet verified:** Firmware builds and hardware operation, ROS 2 builds and visualization, and kinematic parameters.

## README Maintenance

Whenever an AI assistant modifies project files, it must update this README and the [Chinese version](readme-cn.md) before completing the task. Updates must cover the relevant content, last updated date, and change log. Both versions must remain aligned, without requiring another reminder. The full rules are maintained in [AGENTS.md](AGENTS.md).

Use this `Robotic Arm/` directory as the Codex project working directory. `AGENTS.md` is the default project instruction entry point and contains the complete collaboration rules. See the [official OpenAI documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md) for instruction discovery details.

This maintenance rule runs as part of an AI editing task. Saving files manually in CAD software, an IDE, or another application does not trigger a README update by itself.

## Change Log

| Date | Files | Changes | Verification |
| --- | --- | --- | --- |
| 2026-09-13 | `readme-cn.md`, `readme-en.md` | Simplified both project descriptions as requested, keeping entry points and verification status aligned. | Checked corresponding content, dates, language links, and local links. |
| 2026-09-12 | `readme-en.md`, `readme.md`, `AGENTS.md` | Added a complete English README and links between the two language versions. Extended the README maintenance rules to require updates to both versions after each change. | Checked corresponding sections, project information, change logs, and local documentation links. Documentation changes only; no builds, simulations, or hardware tests were run. |
| 2026-09-12 | `AGENTS.md`, `readme.md` | Added project documentation. Merged both Agent documents into a single `AGENTS.md` and removed `Agent.md`, retaining the full requirement to update the README after each change. Documented the current entry points and unverified items. | Statically checked project files, the merged rules, and local links. No builds, simulations, or hardware tests were run. |
