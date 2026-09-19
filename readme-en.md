---
tags:
  - Project
Finish: false
date: 2026-09-12
---

# Robotic Arm

[简体中文](readme-cn.md) | **English**

A robotic arm project workspace containing mechanical models and 3D printing resources, an STM32F103 firmware project, and D-H and URDF reference files.

Last updated: 2026-09-19

## Project Structure

| Directory or file | Purpose | Main entry points |
| --- | --- | --- |
| `1. Model/` | STEP models, 3D printing files, and assembly instructions | [ZERO_ARM.STEP](<1. Model/STEP/ZERO_ARM.STEP>), [3d_printing_all.3mf](<1. Model/3d_printing_all.3mf>), [Assembly guide](<1. Model/installation_guide.md>) |
| `1. Model/OVO/` | OVO assembly and references, 13-item STEP sample, and original working-copy archive | [Folder guide](<1. Model/OVO/README.md>), [OVO assembly](<1. Model/OVO/CAD/ZERO_ARM_OVO.SLDASM>) |
| `2. Software/` | STM32CubeIDE firmware project, including HAL and FreeRTOS | [robot_f103.ioc](<2. Software/robot_f103.ioc>), [main.c](<2. Software/Core/Src/main.c>), [freertos.c](<2. Software/Core/Src/freertos.c>) |
| `3. Simulink/` | MATLAB initialization script, D-H table, and URDF resources | [robot_run.m](<3. Simulink/robot_run.m>), [D-H.md](<3. Simulink/D-H.md>) |
| `3. Simulink/URDF/exported/zero_arm_description/` | ROS 2 robot description package named `zero_arm_description` | [URDF](<3. Simulink/URDF/exported/zero_arm_description/urdf/zero_arm_description.urdf>), [Display launch file](<3. Simulink/URDF/exported/zero_arm_description/launch/display.launch.py>), [package.xml](<3. Simulink/URDF/exported/zero_arm_description/package.xml>) |
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

`URDF/exported/zero_arm_description/` is the current ROS 2 description package. Its `package.xml` declares dependencies including `ament_cmake`, `robot_state_publisher`, `joint_state_publisher_gui`, and `rviz2`. `display.launch.py` provides entry points for robot state publishing, a joint slider interface, and RViz visualization. Prepare a compatible ROS 2 environment and build the package before use.

From this project's `3. Simulink/` directory, locate the final model with `pkg = fullfile(pwd, 'URDF', 'exported', 'zero_arm_description');`. See the [URDF instructions](<3. Simulink/URDF/README.md>) for import commands. `robot_run.m` itself does not import the URDF.

## Status and Next Steps

- **OVO coordinate correction:** The fresh STEP assembly was split into 50 components and seven rigid bodies, and the user imported the structure package into urdf.online. Its edited preview showed inconsistent mesh/joint coordinates. Fresh STEP geometry has now been rebuilt as joint-local meshes in a [Z-up six-axis URDF validation package](<3. Simulink/URDF_OVO_20260919/ZERO_ARM_upright_6axis_urdf.zip>). Checks passed for 7 links, 6 revolute joints, mesh references, ZIP CRC, inertia structure and 24 poses against the previous six-axis reference. Joint parameters come from that reference; mass and limits remain placeholders. Browser reimport shows an upright, connected robot. Each slider was tested at +10.8 degrees, then all were reset to zero. Downstream motion was visible for joints 1–5; nearly axisymmetric tool geometry limits visual confirmation of joint 6 direction. The [browser round-trip package](<3. Simulink/URDF_OVO_20260919/ZERO_ARM_urdf_online_verified.zip>) preserves all seven mesh files byte-for-byte and equivalent parsed URDF content. The user supplied a successful MATLAB import/zero-pose screenshot; full joint details and motion are pending. Simulink and hardware were not run. See the [process and validation record](<3. Simulink/URDF_OVO_20260919/README.md>).

- **New export:** The [2026-09-17 six-axis URDF](<3. Simulink/URDF/README.md>) was independently re-extracted from the current CAD, correcting stale mesh-name collisions: 7 links, 6 joints and 50 STL files. Zero-pose geometry, mesh references and merged inertia checks passed; browser appearance was inspected. The user successfully ran MATLAB `importrobot` and confirmed the zero-pose appearance; command output reports 6 bodies. Full joint details and individual joint motion remain unconfirmed. `smimport` and Simulink simulation have not been performed; joint limits and mass properties still require calibration. The incorrect old `UDRT/` was deleted as requested.

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
| 2026-09-19 | `1. Model/OVO/`, workflow path references, both READMEs | Consolidated OVO files: Pack and Go collected the assembly, available references and Toolbox bearing into CAD (22 files); archived the 15 sample exports and original working copy separately. Resources in 3. Simulink stay in place. | SHA-256 unchanged for all 16 moved files; 13 relative STEP references valid. The relocated assembly opened and displayed; main reference paths checked. Pre-existing missing historical references remain; full design-reference completeness is not claimed. |
| 2026-09-19 | `1. Model/OVO/CAD/ZERO_ARM_OVO.SLDASM`, OVO samples, `3. Simulink/URDF_OVO_20260919/`, both READMEs | Freshly exported STEP, split 50 components into seven groups, recorded browser coordinate issues, and added local-mesh rebuilding, a Z-up six-axis URDF and validation report; documented the actual SW/OVO/URDF workflow and MATLAB path correction. | Identity/mass conservation, 7 links/6 joints, ZIP/references, inertia structure and 24 reference poses passed. Browser reimport and six slider checks completed and reset to zero; joint 6 direction remains visually inconclusive. Browser export preserves meshes and parsed XML. The user supplied a successful MATLAB import/zero-pose screenshot; full joint details and motion are pending. Simulink and hardware were not run. |
| 2026-09-18 | Both READMEs, `3. Simulink/URDF/README.md` | Updated current entry paths to the existing `URDF/` directory and recorded user-confirmed MATLAB import and zero-pose appearance. Joint motion, Simulink and hardware checks remain pending. | Checked current file paths; MATLAB status is based on user output and screenshot. Documentation changes only in this update. |
| 2026-09-17 | `3. Simulink/URDF_export_20260917/`, old `UDRT/`, both READMEs | Deleted the incorrect old `UDRT/` as requested and updated entry links. Preserved the old export snapshot, re-extracted CAD, rebuilt the six-axis chain and exported a separate URDF/STL package with rebuild scripts and validation records. | 7 links, 6 joints, 50 meshes; CAD zero-pose geometry and final inertia structure checks passed. MATLAB, Simulink and hardware were not run. |
| 2026-09-13 | `readme-cn.md`, `readme-en.md` | Simplified both project descriptions as requested, keeping entry points and verification status aligned. | Checked corresponding content, dates, language links, and local links. |
| 2026-09-12 | `readme-en.md`, `readme.md`, `AGENTS.md` | Added a complete English README and links between the two language versions. Extended the README maintenance rules to require updates to both versions after each change. | Checked corresponding sections, project information, change logs, and local documentation links. Documentation changes only; no builds, simulations, or hardware tests were run. |
| 2026-09-12 | `AGENTS.md`, `readme.md` | Added project documentation. Merged both Agent documents into a single `AGENTS.md` and removed `Agent.md`, retaining the full requirement to update the README after each change. Documented the current entry points and unverified items. | Statically checked project files, the merged rules, and local links. No builds, simulations, or hardware tests were run. |
