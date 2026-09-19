---
tags:
  - Project
Finish: false
date: 2026-09-12
---

# Robotic Arm

**简体中文** | [English](readme-en.md)

机械臂项目工作区，包含机械模型与打印资源、STM32F103 固件工程、D-H 与 URDF 资料。

最后更新：2026-09-19

## 项目目录 / Project Structure

| 目录或文件 | 用途 | 主要入口 |
| --- | --- | --- |
| `1. Model/` | STEP 模型、3D 打印文件与装配说明 | [ZERO_ARM.STEP](<1. Model/STEP/ZERO_ARM.STEP>)、[3d_printing_all.3mf](<1. Model/3d_printing_all.3mf>)、[安装教程](<1. Model/installation_guide.md>) |
| `1. Model/OVO/` | OVO 装配体及引用、13 件 STEP 样包和原工作副本归档 | [收纳说明](<1. Model/OVO/README.md>)、[OVO 装配体](<1. Model/OVO/CAD/ZERO_ARM_OVO.SLDASM>) |
| `2. Software/` | STM32CubeIDE 固件工程，含 HAL 与 FreeRTOS | [robot_f103.ioc](<2. Software/robot_f103.ioc>)、[main.c](<2. Software/Core/Src/main.c>)、[freertos.c](<2. Software/Core/Src/freertos.c>) |
| `3. Simulink/` | MATLAB 初始化脚本、D-H 表和 URDF 资源 | [robot_run.m](<3. Simulink/robot_run.m>)、[D-H.md](<3. Simulink/D-H.md>) |
| `3. Simulink/URDF/exported/zero_arm_description/` | ROS 2 机器人描述包，包名为 `zero_arm_description` | [URDF](<3. Simulink/URDF/exported/zero_arm_description/urdf/zero_arm_description.urdf>)、[显示启动文件](<3. Simulink/URDF/exported/zero_arm_description/launch/display.launch.py>)、[package.xml](<3. Simulink/URDF/exported/zero_arm_description/package.xml>) |
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

`URDF/exported/zero_arm_description/` 是当前 ROS 2 描述包。其 `package.xml` 声明 `ament_cmake`、`robot_state_publisher`、`joint_state_publisher_gui`、`rviz2` 等依赖；`display.launch.py` 提供机器人状态发布、关节滑块界面和 RViz 显示入口。使用前需准备相应 ROS 2 环境并构建该包。

从本项目 `3. Simulink/` 目录读取最终模型：`pkg = fullfile(pwd, 'URDF', 'exported', 'zero_arm_description');`。完整导入命令见 [URDF 说明](<3. Simulink/URDF/README.md>)。`robot_run.m` 本身不执行 URDF 导入。

## 当前状态与待办 / Status and Next Steps

- **OVO 新包坐标修正：** 从新 STEP 拆分的 50 个组件已归为七个刚体；用户已将结构包导入 urdf.online。网页编辑预览出现网格与关节坐标不一致，现已从 STEP 重新生成关节局部网格，提供 [Z 轴向上六轴 URDF 校验包](<3. Simulink/URDF_OVO_20260919/ZERO_ARM_upright_6axis_urdf.zip>)。7 连杆、6 转动关节、网格引用、ZIP CRC、惯量结构和 24 组姿态与旧六轴参考的数值对照通过。关节参数沿用旧参考，质量与限位仍为占位；网页重新导入显示整机竖直且连续，六轴滑块逐一测试 +10.8° 并回零；前五轴下游运动可见，第六轴近轴对称外观使自转方向尚不易确认。已保存 [网页回存包](<3. Simulink/URDF_OVO_20260919/ZERO_ARM_urdf_online_verified.zip>)，七个网格逐字节一致、URDF 解析内容一致；用户已提供 MATLAB 新包导入与零位成功截图，完整关节明细/运动待确认；Simulink 与硬件未运行。详见 [过程与检查记录](<3. Simulink/URDF_OVO_20260919/README.md>)。

- **新导出：** [2026-09-17 六轴 URDF](<3. Simulink/URDF/README.md>) 已从当前 CAD 独立重新提取，修复旧网格编号错配；7 连杆、6 关节、50 STL。零位几何、网格引用及合并惯量检查通过，浏览器显示已核对；用户已在 MATLAB 成功执行 `importrobot` 并确认零位外观，命令输出显示 6 bodies；完整关节明细和逐关节运动尚待确认，`smimport` 与 Simulink 仿真尚未进行，关节限位和质量参数待标定。错误的旧 `UDRT/` 已按用户要求删除。

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
| 2026-09-19 | `1. Model/OVO/`、流程路径说明、两版 README | 将 OVO 相关文件统一收纳：CAD 内通过 Pack and Go 打包装配体、可用引用与 Toolbox 轴承，共 22 个文件；STEP 样包 15 件及原副本分别归档。3. Simulink 资源位置不变。 | 16 个移动文件 SHA-256 一致，13 个 STEP 相对引用有效；新位置装配体已打开显示并检查主要引用路径。原有缺失历史参考仍保留，未宣称全部设计参考完整。 |
| 2026-09-19 | `1. Model/OVO/CAD/ZERO_ARM_OVO.SLDASM`、OVO 样包、`3. Simulink/URDF_OVO_20260919/`、两版 README | 新导出整机 STEP，拆分 50 件并归为七组；记录网页坐标问题，新增局部网格重建脚本、Z 向上六轴 URDF 与校验报告，并整理实际 SW/OVO/URDF 转化流程及 MATLAB 路径修正。 | 50 件匹配与质量守恒通过；7 连杆/6 关节、ZIP/引用、惯量结构、24 组姿态参考对照通过。网页重导入及六轴滑块检查完成并回零；第六轴视觉方向仍有限制。网页回存网格/XML 一致；用户已提供 MATLAB 新包导入与零位成功截图，完整关节明细/运动待确认；Simulink 与硬件未运行。 |
| 2026-09-18 | 两版 README、`3. Simulink/URDF/README.md` | 按现有目录将当前入口更新为 `URDF/`，记录用户完成 MATLAB 导入及零位外观确认；保留关节运动、Simulink 和硬件待验证状态。 | 已核对当前文件路径；MATLAB 状态依据用户输出和截图，本次仅更新文档。 |
| 2026-09-17 | `3. Simulink/URDF_export_20260917/`、旧 `UDRT/`、两版 README | 按用户要求删除错误的旧 `UDRT/` 并更新入口链接；保存旧导出快照，重新提取 CAD，重建六轴连接并导出独立 URDF/STL 包，附重建脚本和检查记录。 | 7 连杆、6 关节、50 网格；CAD 零位几何与最终惯量结构检查通过。未运行 MATLAB、Simulink 或硬件。 |
| 2026-09-13 | `readme-cn.md`、`readme-en.md` | 按用户要求精简两版项目说明，保持目录入口与验证状态对应。 | 已核对两版内容、日期、语言切换与本地链接。 |
| 2026-09-12 | `readme-en.md`、`readme.md`、`AGENTS.md` | 添加完整英文 README 和中英文切换链接；将每次修改后的 README 同步规则扩展为中英文两版。 | 已核对两版章节、项目信息与变更记录，检查文档本地链接。仅修改文档，未执行构建、仿真或硬件测试。 |
| 2026-09-12 | `AGENTS.md`、`readme.md` | 新增项目说明；将两份 Agent 文档合并为单一 `AGENTS.md` 并移除 `Agent.md`；保留每次修改后同步 README 的完整规则；记录当前工程入口与待验证状态。 | 已静态核对项目文件，检查合并后的规则与本地链接。未执行构建、仿真或硬件测试。 |
