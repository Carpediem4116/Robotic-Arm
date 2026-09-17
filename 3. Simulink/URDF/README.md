# ZERO_ARM URDF 导出（2026-09-17）

交付文件：`exported/zero_arm_description/urdf/zero_arm_description.urdf`；便携包：`zero_arm_description.zip`。

来源为当前 SolidWorks 会话中的 `Robotic Arm/1. Model/ZERO_ARM.SLDASM`，使用 sw2robot 0.4.4 在 `clean/ZERO_ARM` 重新提取，未改写原装配体。错误的旧 `3. Simulink/UDRT/` 已按用户后续要求删除。本目录根下的旧 graph/meshes/YAML 是操作前快照，不是最终导出；后续重建请使用 `clean/ZERO_ARM`。

修复了旧 YAML 和缓存中的短名称碰撞：旧 c_1_2/c_1_3 对应的夹具、固定爪网格与当前 CAD 不一致。新配置以 frame0 为底座，CAD +Y 映射为 URDF +Z。将固定零件合并后得到 base_link、link_1 至 link_6，以及 joint_1 至 joint_6。同步轮、紧固件按所属连杆固定，属于六轴运动学简化，不模拟传动内部运动。

## 检查结果

- 7 links、6 revolute joints、50 个 STL 文件，网格引用均存在；六关节形成连续串联链。
- 已在 sw2robot 打开最终 URDF，确认直立方向、底座固定爪及末端夹具显示。
- 50 个顶层 CAD 零件的零位网格顶点与导出结果最大偏差约 7.83e-9 m。
- 子装配采样检查按 3DXML 毫米→米换算后无缺失项。sw2robot 原检查仍会提示 20 个子零件缺失；其原生 3DXML 顶点检查未进行这一步单位换算，不应直接据此判定最终网格缺失。
- 整体装配预览 3DXML 存在实例数告警；URDF 使用的是单独导出的零件网格，未使用该整体预览网格。
- 原 CAD frame3 惯量有三角不等式告警；合并固定零件后的 7 个最终惯量矩阵均为正定并满足主惯量三角不等式。真实质量、密度及惯量精度未标定。
- `validation.json` 保存具体检查值，`verify_export.py` 可复核；`build_export.py` 重建独立导出包。

## MATLAB 下一步

在 MATLAB 将当前目录设为此 `URDF_export_20260917` 目录，然后执行：

```matlab
pkg = fullfile(pwd, 'exported', 'zero_arm_description');
robot = importrobot(fullfile(pkg, 'urdf', 'zero_arm_description.urdf'), ...
    'MeshPath', fullfile(pkg, 'meshes'));
show(robot);
showdetails(robot);
```

本次尚未运行 MATLAB importrobot/smimport、Simulink 或实物。六个关节暂用 ±π rad 占位限位；正方向、编码器零位及硬件实际限位需后续标定，不能直接用来驱动实物。
