# OVO 文件收纳

整理日期：2026-09-19。范围仅为 `1. Model` 中的 OVO 工作副本和导出样包。

| 位置 | 用途 |
| --- | --- |
| [CAD/ZERO_ARM_OVO.SLDASM](CAD/ZERO_ARM_OVO.SLDASM) | 今后打开的 OVO 装配体；通过 SolidWorks Pack and Go 收纳可找到的 CAD 引用，包含 Toolbox 轴承。CAD 文件夹共 22 个文件，另有装配体内置虚拟零件。 |
| [OVO_STEP_20260919/](OVO_STEP_20260919/) | 13 个 STEP、`mass_props.json` 和原 ZIP，共 15 个文件。这是 OVO 格式样包，不是完整六轴机械臂。 |
| [Source/ZERO_ARM_OVO.SLDASM](Source/ZERO_ARM_OVO.SLDASM) | 移动前工作副本的原样归档；保留旧引用，仅用于追溯或恢复，日常打开上面的 CAD 副本。 |

16 个移动文件的 SHA-256 在移动前后保持一致，JSON 中的 13 个相对 STEP 引用有效。`mass_props.json` 的 `source_file` 保留导出时的历史路径，未改写原始导出数据。

Pack and Go 列表原先已有找不到的历史引用，例如电机/减速器的源 STEP 和 `XG_Robot_Arm.SLDASM`。此次收纳没有修复这些历史关联，不能据此宣称所有外部设计参考均完整。新位置的装配体已实际打开并显示；主要 CAD 引用路径已检查。

原始 `../ZERO_ARM.SLDASM` 及其共享零件留在原目录。最终 URDF、整机 STEP、重建脚本仍位于 [../../3. Simulink/URDF_OVO_20260919/](<../../3. Simulink/URDF_OVO_20260919/>)，MATLAB 导入路径不变。

原样归档 SHA-256：`8F847C19146DE4764F3FA8AFEECBC03D08E5B6CA00F51408FCF66AD0BA904FD7`。
