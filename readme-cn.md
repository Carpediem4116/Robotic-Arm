---
tags:
  - Project
Finish: false
date: 2026-09-12
---

# Robotic Arm

**简体中文** | [English](readme-en.md)

机械臂项目工作区，包含机械模型与打印资源、STM32F103 固件工程、D-H 与 URDF 资料。

最后更新：2026-09-13

## 项目目录 / Project Structure

| 目录或文件 | 用途 | 主要入口 |
| --- | --- | --- |
| `1. Model/` | STEP 模型、3D 打印文件与装配说明 | [ZERO_ARM.STEP](<1. Model/STEP/ZERO_ARM.STEP>)、[3d_printing_all.3mf](<1. Model/3d_printing_all.3mf>)、[安装教程](<1. Model/installation_guide.md>) |
| `2. Software/` | STM32CubeIDE 固件工程，含 HAL 与 FreeRTOS | [robot_f103.ioc](<2. Software/robot_f103.ioc>)、[main.c](<2. Software/Core/Src/main.c>)、[freertos.c](<2. Software/Core/Src/freertos.c>) |
| `3. Simulink/` | MATLAB 初始化脚本、D-H 表和 URDF 资源 | [robot_run.m](<3. Simulink/robot_run.m>)、[D-H.md](<3. Simulink/D-H.md>) |
| `3. Simulink/UDRT/` | ROS 2 机器人描述包，包名为 `zero_arm_description` | [URDF](<3. Simulink/UDRT/urdf/zero_arm_description.urdf>)、[显示启动文件](<3. Simulink/UDRT/launch/display.launch.py>)、[package.xml](<3. Simulink/UDRT/package.xml>) |
| `AGENTS.md` | 统一的项目协作、验证与 README 同步规则，也是 Codex 项目指令入口 | [阅读规则](AGENTS.md) |

## 使用入口 / Getting Started

### 机械模型 / Mechanical Model

使用支持 STEP 的 CAD 软件查看 `1. Model/STEP/`；使用支持 3MF 的切片软件打开打印文件。装配前结合实际零件核对安装教程。

### 固件工程 / Firmware

使用 STM32CubeIDE 导入 `2. Software/` 中已有的工程配置，查看 `robot_f103.ioc`、`Core/Src/main.c` 和 `Core/Src/freertos.c`。

当前 `.ioc` 指定 **STM32F103VET6**，目标工具链为 **STM32CubeIDE**。`main.c` 初始化 GPIO、DMA、CAN、USART1、USART3 和 RTOS；默认任务每隔 500 ms 翻转一次红色 LED。固件的运行与机械臂控制能力需要分别验证。

### MATLAB 与机器人描述 / MATLAB and Robot Description

在 MATLAB 中将当前文件夹设为本项目的 `3. Simulink/`，再运行 `robot_run.m`。脚本会清理工作区、命令窗口并添加当前目录及子目录到搜索路径；运行前保存需要保留的工作区数据。

当前脚本没有加载模型或调用 `sim`，本项目内尚未找到 `.slx` 或 `.mdl` 文件。`D-H.md` 用于查看运动学参数，参数在实际模型中的绑定与验证仍需单独完成。

`UDRT/` 是 ROS 2 描述包。其 `package.xml` 声明 `ament_cmake`、`robot_state_publisher`、`joint_state_publisher_gui`、`rviz2` 等依赖；`display.launch.py` 提供机器人状态发布、关节滑块界面和 RViz 显示入口。使用前需准备相应 ROS 2 环境并构建该包。

## 当前状态与待办 / Status and Next Steps

- **已核对：** 目录结构、主要入口、F103 工程配置、默认任务及 MATLAB 脚本内容。
- **待补齐：** 安装教程引用的 `4. Other/Images/` 在本工程内不存在，教程插图目前缺失。
- **待补齐：** 若要进行 Simulink 仿真，需补充实际模型和对应运行入口。
- **待验证：** 固件构建与硬件运行、ROS 2 构建与显示、运动学参数。

## README 维护规则 / README Maintenance

每次由 AI 助手修改本项目的文件后，助手必须在本次任务结束前同步更新本 README 和 [英文版](readme-en.md)，包括相关正文、最后更新日期和变更记录；两版内容须保持对应，无需再次提醒。详细要求统一维护在 [AGENTS.md](AGENTS.md)。

建议将本 `Robotic Arm/` 文件夹作为 Codex 项目的工作目录。`AGENTS.md` 是默认项目指令入口，直接包含完整协作规则；文件发现机制见 [OpenAI 官方说明](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。

这是一项随 AI 修改任务执行的文档维护规则。手动在 CAD、IDE 或其他软件中保存文件不会自行触发 README 更新。

## 变更记录 / Change Log

| 日期 | 涉及文件 | 变更内容 | 验证结果 |
| --- | --- | --- | --- |
| 2026-09-13 | `readme-cn.md`、`readme-en.md` | 按用户要求精简两版项目说明，保持目录入口与验证状态对应。 | 已核对两版内容、日期、语言切换与本地链接。 |
| 2026-09-12 | `readme-en.md`、`readme.md`、`AGENTS.md` | 添加完整英文 README 和中英文切换链接；将每次修改后的 README 同步规则扩展为中英文两版。 | 已核对两版章节、项目信息与变更记录，检查文档本地链接。仅修改文档，未执行构建、仿真或硬件测试。 |
| 2026-09-12 | `AGENTS.md`、`readme.md` | 新增项目说明；将两份 Agent 文档合并为单一 `AGENTS.md` 并移除 `Agent.md`；保留每次修改后同步 README 的完整规则；记录当前工程入口与待验证状态。 | 已静态核对项目文件，检查合并后的规则与本地链接。未执行构建、仿真或硬件测试。 |
