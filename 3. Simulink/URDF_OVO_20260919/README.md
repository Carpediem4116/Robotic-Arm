# ZERO_ARM 新 STEP 拆分与 OVO 结构包（2026-09-19）

本目录是从当前 SolidWorks 工作副本新导出的几何。用户已导入七组结构包；发现网页编辑预览的坐标不一致后，从新 STEP 重建了 Z 轴向上的六轴 URDF 校验包。文件、数值及网页重新导入检查通过；已测试六轴滑块并回零。前五轴下游运动可见且未散开，第六轴因末端近轴对称，外观自转方向未充分确认。用户随后已提供 MATLAB 新包导入与零位成功显示截图；完整关节明细与 MATLAB 运动检查待确认。

## 使用哪个文件

- **网页回存包：`ZERO_ARM_urdf_online_verified.zip`**。由网页下载后无损重新压缩，七个 STL 与输入包逐字节一致，URDF 解析内容一致。

- **当前重新导入：`ZERO_ARM_upright_6axis_urdf.zip`**。含 `zero_arm_ovo.urdf` 和七个关节局部 STL；未压缩版本在 `upright_urdf/`。
- `build_upright_urdf.py`：从新 STEP 重建 STL、将 CAD +Y 映射到 URDF +Z、构建六轴链并校验。
- `upright_validation.json`：本次文件与数值检查结果。

- `ZERO_ARM_grouped_7_step.zip`：原始七组结构包，已由用户在 urdf.online 导入。包含底座与六段运动连杆，七个 STEP 和 `mass_props.json`，目前没有关节轴数据。
- `ZERO_ARM_individual_50_step.zip`：保留全部 50 个顶层组件实例，方便重新分组；含 50 个 STEP 和 JSON。
- `grouping_report.json`：逐件身份、目标组、变换误差和质量守恒检查。
- `assembly_tree.json`：新 STEP 的完整命名装配树。
- `ZERO_ARM_OVO_RAW.STEP`：2026-09-19 新导出的完整 STEP AP214。
- `ZERO_ARM_OVO_RAW.STEP.SLDASM`：导出过程中另存的原生装配体检查点，**不是 STEP**；几何提取读取的是上面的 `.STEP` 文件。
- `ovo_sample_13/`：OVO 直接导出的 13 项格式样包，不包含完整机械臂。
- `individual_50/` 与 `grouped_7/`：未压缩的逐件和七组结构包。

## 来源与验证

1. OVO 工作副本现收纳为 `../../1. Model/OVO/CAD/ZERO_ARM_OVO.SLDASM`；原样副本归档于 `../../1. Model/OVO/Source/`，本目录资源与 MATLAB 导入路径未移动。实际以 SolidWorks 的“文件 → 另存为 → STEP AP214”重新输出整机，默认坐标系、实体/曲面几何；隐藏/压缩组件提示选择“否”，保留当前配置。
2. 用 STEPCAF 读取 50 个顶层组件，包括四个底座固定爪。电机子装配保持其导出几何，不再拆内部小零件。
3. 旧 `../URDF/clean/ZERO_ARM/graph.json` 只用于零件身份对照；同时校验名称和装配变换，50 项一对一匹配。最大变换元素差约 `4.55e-15`（平移已统一到米）。
4. 分组参考旧 `ZERO_ARM.joints.yaml` 的六轴简化。各组成员数依次为 `9, 9, 10, 4, 9, 7, 2`。新几何没有从旧 STL/ZIP 复制。
5. 两个 ZIP 的 CRC 和 STEP 引用检查通过。抽查重新读取的 STEP 能保留世界位姿。小电机新拆分 STEP 与 OVO 的独立 STEP 体积和质心一致。
6. 所有质量都明确使用 **1000 kg/m³ 占位密度**。逐件重新计算，分组惯量用平行轴定理合并；总质量占位值约 `1.70458065 kg`，分组前后质量差为零。不能用于已校准的动力学结论。
7. OVO 的小电机 JSON 质量比其 STEP 按相同密度计算值高约 `0.00207370 kg`，质心最大差约 `0.000962575 m`，原因未确认。未强行把两者视为一致。

## 可重复执行

依赖使用 OVO 已安装环境的 `OCP`、`numpy`、`yaml`。

```powershell
$ovoPython = 'C:\Users\SH\AppData\Local\OVO-URDF-工具\simplify-factory\.venv\Scripts\python.exe'
& $ovoPython .\inspect_step.py .\ZERO_ARM_OVO_RAW.STEP --output .\assembly_tree.json
& $ovoPython .\split_and_group.py
```

第二条命令会重建本目录的逐件 STEP、分组 STEP、JSON、ZIP 和检查报告。不会修改源 CAD 或旧 URDF。

## 坐标修正与验证边界

原始 STEP 以 CAD Y 轴为竖直方向。网页编辑器中直接补写关节和 visual 原点后，预览网格散开；下载的网格顶点也与原 CAD 全局坐标不同。该编辑路径存在坐标重映射，不能只按普通 URDF 文本变换处理并宣称完成。下载目录中的 `ZERO_ARM_OVO_RAW_urdf.zip` 是这次失败预览的诊断产物，不作为交付文件。

当前脚本重新读取七组 STEP，采用 `p_world = Rx(pi/2) * p_CAD`，每个 STL 保存 `p_local = p_world - joint_origin_world`。所有 visual/collision 原点均为零，关节零位坐标系轴向统一为世界轴向；质心和惯量同步转换，惯量直接使用 OCP 分组张量，不沿用网页 XML 的非对角符号转换。底座下缘 z=-0.013 m 保留 CAD 原点定义，并非严格地面接触坐标。

关节轴心和轴方向来自旧六轴 URDF，对应的 50 件身份/装配变换已核对。24 组姿态比较轴心及轴方向，最大数值差约 7.81e-13；这只验证重建前后运动学一致，不是新的硬件标定。7 个连杆、6 个 revolute、单根串联树、所有网格引用、ZIP CRC、惯量正定与主惯量三角不等式检查通过。总质量仍为密度 1000 kg/m³ 的占位值。

重新生成：`& $ovoPython .\build_upright_urdf.py`。

## 待完成

- 第六轴自转方向的更清晰视觉或 MATLAB 坐标验证；网页已逐轴设置 +10.8°，测试结束全部回零。
- 材料/质量、限位、速度与力矩标定。
- MATLAB 完整逐关节明细及运动验证；用户已确认新包导入和零位显示。
- Simscape/Simulink 仿真及硬件运行均未进行。
