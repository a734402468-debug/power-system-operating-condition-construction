# 十二题正式批次：完整任务卡

题面和数值在任何正式请求前冻结。以下直接复制冻结原文；独立正确规格不进入模型请求。

## T1

沿用已验证的两集合目录；相对旧CG-T1取消L1固定、转移量改为0.30 MW，全部成员自由协调。

T1：在同一总负荷输入下构造不同负荷分布，供稳态潮流对比及算法测试。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为CG_BASELINE_V1。
C1：统计集合A={L1,L2,L3}，B={L4,L5,L6}；仅final，A有功输入和相对基准减少0.3 MW，B增加同量。固定成员仍参与原集合的基准及最终总量统计。
C2：组内自由协调，不要求比例分配或等量调整。
C3：所列全部负荷{L1,L2,L3,L4,L5,L6}的有功输入总和相对同一基准保持，适用于baseline及every_accepted_state（含final）；总和容差独立于转移两侧容差。
C4：全部六负荷各自保持基准Q/P，P=P0×alpha、Q=Q0×alpha，从基准计算不累乘；适用于baseline及every_accepted_state（含final）。
C5：只允许调整L1（lod_100_1）、L2（lod_101_1）、L3（lod_102_1）、L4（lod_103_1）、L5（lod_104_1）、L6（lod_105_1），其alpha∈[0.99,1.02]；固定输入为无，固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（100 Glen Lyn）∈[1.0119999877014882,1.021999987701488] pu；baseline及every_accepted_state（含final）。
V2（101 Wythe）∈[0.981385013072658,0.991385013072658] pu；baseline及every_accepted_state（含final）。
V3（102 Smythe）∈[0.9762397545453265,0.9862397545453265] pu；baseline及every_accepted_state（含final）。
V4（103 Claytor）∈[1.0050000181018235,1.0150000181018233] pu；baseline及every_accepted_state（含final）。
V5（104 Hancock）∈[0.9660000425318596,0.9760000425318596] pu；baseline及every_accepted_state（含final）。
V6（105 Roanoke）∈[0.9600000003123973,0.9700000003123973] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=1.3636184692382813e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=3.3364502601314728e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu。不重复叠加存储预算；求解残差检查不放宽物理端点。


## T2

复用历史固定成员转移结构；本批重新生成与验收，不称独立盲测。0.20 MW低于剩余转出容量。

T2：保留大负荷L1输入，检查其余负荷是否能完成指定转移；固定成员仍计入A统计。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为CG_BASELINE_V1。
C1：统计集合A={L1,L2,L3}，B={L4,L5,L6}；仅final，A有功输入和相对基准减少0.2 MW，B增加同量。固定成员仍参与原集合的基准及最终总量统计。
C2：组内自由协调，不要求比例分配或等量调整。
C3：所列全部负荷{L1,L2,L3,L4,L5,L6}的有功输入总和相对同一基准保持，适用于baseline及every_accepted_state（含final）；总和容差独立于转移两侧容差。
C4：全部六负荷各自保持基准Q/P，P=P0×alpha、Q=Q0×alpha，从基准计算不累乘；适用于baseline及every_accepted_state（含final）。
C5：只允许调整L2（lod_101_1）、L3（lod_102_1）、L4（lod_103_1）、L5（lod_104_1）、L6（lod_105_1），其alpha∈[0.99,1.02]；固定输入为L1（lod_100_1），固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（100 Glen Lyn）∈[1.0119999877014882,1.021999987701488] pu；baseline及every_accepted_state（含final）。
V2（101 Wythe）∈[0.981385013072658,0.991385013072658] pu；baseline及every_accepted_state（含final）。
V3（102 Smythe）∈[0.9762397545453265,0.9862397545453265] pu；baseline及every_accepted_state（含final）。
V4（103 Claytor）∈[1.0050000181018235,1.0150000181018233] pu；baseline及every_accepted_state（含final）。
V5（104 Hancock）∈[0.9660000425318596,0.9760000425318596] pu；baseline及every_accepted_state（含final）。
V6（105 Roanoke）∈[0.9600000003123973,0.9700000003123973] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=1.3636184692382813e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=3.3364502601314728e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu。不重复叠加存储预算；求解残差检查不放宽物理端点。


## T3

相对NJ-T1自由分配，增加仅final组内同倍率政策；转移量保留0.415 MW。

T3：构造两组按各自基准负荷构成比例分担的最终输入转移工况；不约束过程比例。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为NJ_BASELINE_V1。
C1：统计集合A={L1,L2}，B={L3,L4}；仅final，A有功输入和相对基准减少0.415 MW，B增加同量。固定成员仍参与原集合的基准及最终总量统计。
C2：仅final，A内成员具有相同绝对倍率alpha，B内成员具有相同绝对倍率alpha；两组倍率分别由共同数值工具求解。baseline及其他接受状态不施加这两条比例关系。
C3：所列全部负荷{L1,L2,L3,L4}的有功输入总和相对同一基准保持，适用于baseline及every_accepted_state（含final）；总和容差独立于转移两侧容差。
C4：所列全部负荷各自保持同一参考状态下的Q/P，使用P=P0×alpha、Q=Q0×alpha，从基准计算，禁止累乘；适用于baseline及every_accepted_state（含final）。Seli的负Q保持原有符号和映射，不转换输入模式。
C5：只允许调整L1（Shuf_lod.ElmLod）、L2（Jinx_lod.ElmLod）、L3（Aoy_load.ElmLod）、L4（Seli_lod.ElmLod），其alpha∈[0.99,1.02]；固定输入为无，固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（Shuf115）∈[0.9911242876845122,1.0011242876845121] pu；baseline及every_accepted_state（含final）。
V2（Jinx230）∈[0.9945953542043262,1.0045953542043262] pu；baseline及every_accepted_state（含final）。
V3（Aoy115）∈[0.995860618120925,1.0058606181209249] pu；baseline及every_accepted_state（含final）。
V4（Seli230）∈[1.0133168288134877,1.0233168288134875] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=2.388818359375e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=9.794873805516215e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu。不重复叠加存储预算；求解残差检查不放宽物理端点。


## T4

相对NJ开发题改变集合配对，并采用既有已测20微pu保持判据；不是地理供电区域。

T4：改变统计集合，在0.50 MW转移时限制Shuf115电压扰动，供受控分布变化测试。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为NJ_BASELINE_V1。
C1：统计集合A={L1,L3}，B={L2,L4}；仅final，A有功输入和相对基准减少0.5 MW，B增加同量。固定成员仍参与原集合的基准及最终总量统计。
C2：组内自由协调，不要求比例分配或等量调整。
C3：所列全部负荷{L1,L2,L3,L4}的有功输入总和相对同一基准保持，适用于baseline及every_accepted_state（含final）；总和容差独立于转移两侧容差。
C4：所列全部负荷各自保持同一参考状态下的Q/P，使用P=P0×alpha、Q=Q0×alpha，从基准计算，禁止累乘；适用于baseline及every_accepted_state（含final）。Seli的负Q保持原有符号和映射，不转换输入模式。
C5：只允许调整L1（Shuf_lod.ElmLod）、L2（Jinx_lod.ElmLod）、L3（Aoy_load.ElmLod）、L4（Seli_lod.ElmLod），其alpha∈[0.99,1.02]；固定输入为无，固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（Shuf115）∈[0.9961042876845122,0.9961442876845122] pu；baseline及every_accepted_state（含final）。
V2（Jinx230）∈[0.9945953542043262,1.0045953542043262] pu；baseline及every_accepted_state（含final）。
V3（Aoy115）∈[0.995860618120925,1.0058606181209249] pu；baseline及every_accepted_state（含final）。
V4（Seli230）∈[1.0133168288134877,1.0233168288134875] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=2.388818359375e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=9.794873805516215e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu。不重复叠加存储预算；求解残差检查不放宽物理端点。


## V1

明确复用已成功CG-G1开发任务结构与电压带；本批仅是统一冻结版重复构造，不称新盲测。

V1：构造101 Wythe电压降低0.001至0.0015 pu的稳态测试状态，用于比较电压敏感算法输入。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为CG_BASELINE_V1。
C1：增长组A={L1,L2}，B={L4}，组间增长幅度独立。
C2：仅final，每个非空增长组内采用相同绝对倍率alpha，即相对各自基准有功按原比例增长；保持各自Q/P。连续幅度由共同数值工具求解，不要求组间倍率相同。
C3：本题为负荷增长，不要求负荷有功输入总和守恒，禁止继承旧转移条款。
C4：全部六负荷各自保持基准Q/P，P=P0×alpha、Q=Q0×alpha，从基准计算不累乘；适用于baseline及every_accepted_state（含final）。
C5：只允许调整L1（lod_100_1）、L2（lod_101_1）、L4（lod_103_1），其alpha∈[1.0,1.2]；固定输入为L3（lod_102_1）、L5（lod_104_1）、L6（lod_105_1），固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（100 Glen Lyn）∈[1.0119999877014882,1.021999987701488] pu；baseline及every_accepted_state（含final）。
V2（101 Wythe）∈[0.9848850130726581,0.985385013072658] pu；仅final。
V3（102 Smythe）∈[0.9792397545453265,0.9832397545453265] pu；baseline及every_accepted_state（含final）。
V4（103 Claytor）∈[1.0050000181018235,1.0150000181018233] pu；baseline及every_accepted_state（含final）。
V5（104 Hancock）∈[0.9660000425318596,0.9760000425318596] pu；baseline及every_accepted_state（含final）。
V6（105 Roanoke）∈[0.9600000003123973,0.9700000003123973] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=1.3636184692382813e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=3.3364502601314728e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu。不重复叠加存储预算；求解残差检查不放宽物理端点。


## V2

明确复用CG-G4开发组合，与V1的增长集合、固定项和组数不同。

V2：固定L1/L4/L6，检验不同增长组能否形成101电压目标；无不存在的第二增长组。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为CG_BASELINE_V1。
C1：增长组A={L2,L3,L5}，不存在第二增长组，不输出空对象条款。
C2：仅final，每个非空增长组内采用相同绝对倍率alpha，即相对各自基准有功按原比例增长；保持各自Q/P。连续幅度由共同数值工具求解，不要求组间倍率相同。
C3：本题为负荷增长，不要求负荷有功输入总和守恒，禁止继承旧转移条款。
C4：全部六负荷各自保持基准Q/P，P=P0×alpha、Q=Q0×alpha，从基准计算不累乘；适用于baseline及every_accepted_state（含final）。
C5：只允许调整L2（lod_101_1）、L3（lod_102_1）、L5（lod_104_1），其alpha∈[1.0,1.2]；固定输入为L1（lod_100_1）、L4（lod_103_1）、L6（lod_105_1），固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（100 Glen Lyn）∈[1.0119999877014882,1.021999987701488] pu；baseline及every_accepted_state（含final）。
V2（101 Wythe）∈[0.985185013072658,0.985585013072658] pu；仅final。
V3（102 Smythe）∈[0.9792397545453265,0.9832397545453265] pu；baseline及every_accepted_state（含final）。
V4（103 Claytor）∈[1.0050000181018235,1.0150000181018233] pu；baseline及every_accepted_state（含final）。
V5（104 Hancock）∈[0.9660000425318596,0.9760000425318596] pu；baseline及every_accepted_state（含final）。
V6（105 Roanoke）∈[0.9600000003123973,0.9700000003123973] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=1.3636184692382813e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=3.3364502601314728e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu。不重复叠加存储预算；求解残差检查不放宽物理端点。


## V3

组结构沿用NJ-G1，采用事先按历史0.005探针响应量级登记的0.00010至0.00015 pu降压带；增加明确Jinx保持带。

V3：形成Shuf115小幅降压试验状态，并限制Jinx230变化，用于跨电网电压目标及保留组合测试。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为NJ_BASELINE_V1。
C1：增长组A={L1,L2}，B={L3,L4}，组间增长幅度独立。
C2：仅final，每个非空增长组内采用相同绝对倍率alpha，即相对各自基准有功按原比例增长；保持各自Q/P。连续幅度由共同数值工具求解，不要求组间倍率相同。
C3：本题为负荷增长，不要求负荷有功输入总和守恒，禁止继承旧转移条款。
C4：所列全部负荷各自保持同一参考状态下的Q/P，使用P=P0×alpha、Q=Q0×alpha，从基准计算，禁止累乘；适用于baseline及every_accepted_state（含final）。Seli的负Q保持原有符号和映射，不转换输入模式。
C5：只允许调整L1（Shuf_lod.ElmLod）、L2（Jinx_lod.ElmLod）、L3（Aoy_load.ElmLod）、L4（Seli_lod.ElmLod），其alpha∈[1.0,1.02]；固定输入为无，固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（Shuf115）∈[0.9959742876845122,0.9960242876845122] pu；仅final。
V2（Jinx230）∈[0.9993953542043262,0.9997953542043262] pu；baseline及every_accepted_state（含final）。
V3（Aoy115）∈[0.995860618120925,1.0058606181209249] pu；baseline及every_accepted_state（含final）。
V4（Seli230）∈[1.0133168288134877,1.0233168288134875] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=2.388818359375e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=9.794873805516215e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu。不重复叠加存储预算；求解残差检查不放宽物理端点。


## V4

改变旧NJ-G2分组与固定对象；组内比例仅final，组间连续幅度独立。

V4：固定Aoy输入，令Jinx与Seli同倍率增长，Shuf独立增长，以构造Jinx电压目标。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为NJ_BASELINE_V1。
C1：增长组A={L2,L4}，B={L1}，组间增长幅度独立。
C2：仅final，每个非空增长组内采用相同绝对倍率alpha，即相对各自基准有功按原比例增长；保持各自Q/P。连续幅度由共同数值工具求解，不要求组间倍率相同。
C3：本题为负荷增长，不要求负荷有功输入总和守恒，禁止继承旧转移条款。
C4：所列全部负荷各自保持同一参考状态下的Q/P，使用P=P0×alpha、Q=Q0×alpha，从基准计算，禁止累乘；适用于baseline及every_accepted_state（含final）。Seli的负Q保持原有符号和映射，不转换输入模式。
C5：只允许调整L1（Shuf_lod.ElmLod）、L2（Jinx_lod.ElmLod）、L4（Seli_lod.ElmLod），其alpha∈[1.0,1.02]；固定输入为L3（Aoy_load.ElmLod），固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（Shuf115）∈[0.9960242876845122,0.9962242876845122] pu；baseline及every_accepted_state（含final）。
V2（Jinx230）∈[0.9994153542043263,0.9994753542043262] pu；仅final。
V3（Aoy115）∈[0.995860618120925,1.0058606181209249] pu；baseline及every_accepted_state（含final）。
V4（Seli230）∈[1.0133168288134877,1.0233168288134875] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=2.388818359375e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=9.794873805516215e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu。不重复叠加存储预算；求解残差检查不放宽物理端点。


## L1

明确复用line_scenario_v1/A开发带与组合；不称完全独立测试。

L1：在总输入保持下提高Yonga—Jinx输送水平，为线路观测和联合约束算法提供稳态测试输入。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为NJ_LINE_BASELINE_V1。
C1：仅final，E1（Yonga-Jinx）的c:loading∈[12.842631118996916,12.906208500774126] %。这是模型电流口径的线路负载率，不改额定值，不称拥塞或热安全验证。
C2：可调负荷自由协调，不增加比例或等量约束。
C3：所列全部负荷{L1,L2,L3,L4}的有功输入总和相对同一基准保持，适用于baseline及every_accepted_state（含final）；总和容差独立于转移两侧容差。
C4：所列全部负荷各自保持同一参考状态下的Q/P，使用P=P0×alpha、Q=Q0×alpha，从基准计算，禁止累乘；适用于baseline及every_accepted_state（含final）。Seli的负Q保持原有符号和映射，不转换输入模式。
C5：只允许调整L1（Shuf_lod.ElmLod）、L2（Jinx_lod.ElmLod）、L3（Aoy_load.ElmLod）、L4（Seli_lod.ElmLod），其alpha∈[0.99,1.02]；固定输入为无，固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（Shuf115）∈[0.9911242876845122,1.0011242876845121] pu；baseline及every_accepted_state（含final）。
V2（Jinx230）∈[0.9945953542043262,1.0045953542043262] pu；baseline及every_accepted_state（含final）。
V3（Aoy115）∈[0.995860618120925,1.0058606181209249] pu；baseline及every_accepted_state（含final）。
V4（Seli230）∈[1.0133168288134877,1.0233168288134875] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=2.388818359375e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=9.794873805516215e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu；LINE_LOADING_EDGE_ZERO_V1=0个百分点。不重复叠加存储预算；求解残差检查不放宽物理端点。


## L2

明确复用line_scenario_v1/B的固定负荷组合。

L2：保持Shuf输入，检查其他负荷协调实现相同线路目标。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为NJ_LINE_BASELINE_V1。
C1：仅final，E1（Yonga-Jinx）的c:loading∈[12.842631118996916,12.906208500774126] %。这是模型电流口径的线路负载率，不改额定值，不称拥塞或热安全验证。
C2：可调负荷自由协调，不增加比例或等量约束。
C3：所列全部负荷{L1,L2,L3,L4}的有功输入总和相对同一基准保持，适用于baseline及every_accepted_state（含final）；总和容差独立于转移两侧容差。
C4：所列全部负荷各自保持同一参考状态下的Q/P，使用P=P0×alpha、Q=Q0×alpha，从基准计算，禁止累乘；适用于baseline及every_accepted_state（含final）。Seli的负Q保持原有符号和映射，不转换输入模式。
C5：只允许调整L2（Jinx_lod.ElmLod）、L3（Aoy_load.ElmLod）、L4（Seli_lod.ElmLod），其alpha∈[0.99,1.02]；固定输入为L1（Shuf_lod.ElmLod），固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（Shuf115）∈[0.9911242876845122,1.0011242876845121] pu；baseline及every_accepted_state（含final）。
V2（Jinx230）∈[0.9945953542043262,1.0045953542043262] pu；baseline及every_accepted_state（含final）。
V3（Aoy115）∈[0.995860618120925,1.0058606181209249] pu；baseline及every_accepted_state（含final）。
V4（Seli230）∈[1.0133168288134877,1.0233168288134875] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=2.388818359375e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=9.794873805516215e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu；LINE_LOADING_EDGE_ZERO_V1=0个百分点。不重复叠加存储预算；求解残差检查不放宽物理端点。


## L3

明确复用line_scenario_v1/C；旧无电压限制方案实测变化约3.60e-5 pu，超出本题2e-5 pu带。

L3：线路目标联立Shuf电压保持，用于检验有约束作用的组合构造。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为NJ_LINE_BASELINE_V1。
C1：仅final，E1（Yonga-Jinx）的c:loading∈[12.842631118996916,12.906208500774126] %。这是模型电流口径的线路负载率，不改额定值，不称拥塞或热安全验证。
C2：可调负荷自由协调，不增加比例或等量约束。
C3：所列全部负荷{L1,L2,L3,L4}的有功输入总和相对同一基准保持，适用于baseline及every_accepted_state（含final）；总和容差独立于转移两侧容差。
C4：所列全部负荷各自保持同一参考状态下的Q/P，使用P=P0×alpha、Q=Q0×alpha，从基准计算，禁止累乘；适用于baseline及every_accepted_state（含final）。Seli的负Q保持原有符号和映射，不转换输入模式。
C5：只允许调整L1（Shuf_lod.ElmLod）、L2（Jinx_lod.ElmLod）、L3（Aoy_load.ElmLod）、L4（Seli_lod.ElmLod），其alpha∈[0.99,1.02]；固定输入为无，固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（Shuf115）∈[0.9961042876845122,0.9961442876845122] pu；baseline及every_accepted_state（含final）。
V2（Jinx230）∈[0.9945953542043262,1.0045953542043262] pu；baseline及every_accepted_state（含final）。
V3（Aoy115）∈[0.995860618120925,1.0058606181209249] pu；baseline及every_accepted_state（含final）。
V4（Seli230）∈[1.0133168288134877,1.0233168288134875] pu；baseline及every_accepted_state（含final）。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=2.388818359375e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=9.794873805516215e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu；LINE_LOADING_EDGE_ZERO_V1=0个百分点。不重复叠加存储预算；求解残差检查不放宽物理端点。


## L4

新增第二条已核实线路的保留组合；E2四列响应已存在，不新增采样或控制。

L4：在提高Yonga—Jinx输送的同时限制Jinl—Seli负载率变化，构造线路间保留工况。
这是固定模型中的受控研究任务，集合为登记设备清单，不称实际地理区域。参考状态为NJ_LINE_BASELINE_V1。
C1：仅final，E1（Yonga-Jinx）的c:loading∈[12.842631118996916,12.906208500774126] %。这是模型电流口径的线路负载率，不改额定值，不称拥塞或热安全验证。
C2：可调负荷自由协调，不增加比例或等量约束。
C3：所列全部负荷{L1,L2,L3,L4}的有功输入总和相对同一基准保持，适用于baseline及every_accepted_state（含final）；总和容差独立于转移两侧容差。
C4：所列全部负荷各自保持同一参考状态下的Q/P，使用P=P0×alpha、Q=Q0×alpha，从基准计算，禁止累乘；适用于baseline及every_accepted_state（含final）。Seli的负Q保持原有符号和映射，不转换输入模式。
C5：只允许调整L1（Shuf_lod.ElmLod）、L2（Jinx_lod.ElmLod）、L3（Aoy_load.ElmLod）、L4（Seli_lod.ElmLod），其alpha∈[0.99,1.02]；固定输入为无，固定对象P/Q与基准完全相同。边界及固定条件适用于baseline及every_accepted_state（含final）。其他负荷输入不变。
C6：各电压区间按本母线分别验收：
V1（Shuf115）∈[0.9911242876845122,1.0011242876845121] pu；baseline及every_accepted_state（含final）。
V2（Jinx230）∈[0.9945953542043262,1.0045953542043262] pu；baseline及every_accepted_state（含final）。
V3（Aoy115）∈[0.995860618120925,1.0058606181209249] pu；baseline及every_accepted_state（含final）。
V4（Seli230）∈[1.0133168288134877,1.0233168288134875] pu；baseline及every_accepted_state（含final）。
E2（Jinl-Seli）的c:loading∈[6.677618306764409,6.67961830676441] %，baseline及every_accepted_state（含final）；变化单位为百分点。
所有绝对端点为主验收表示；相对变化由同一端点减同一基准推导，不另行舍入。最终目标不要求baseline已满足。
C7：其他输入、拓扑、共享类型、控制设置及潮流配置不变。保留原平衡及调压机制；配置不变不要求机组连续P/Q不变。不修复已有越限，不宣称全网健康。试算不自动成为接受状态，不解释成动态轨迹。
精度政策：P_SUM_V1=2.388818359375e-05 MW（两侧和总量分别验收）；QP_RESIDUAL_V1=9.794873805516215e-06 Mvar；ALPHA_READ_V1=1e-7；PROP_ALPHA_V1=2e-7；FIXED_EXACT_V1=0；VOLTAGE_EDGE_ZERO_V1=0 pu；LINE_LOADING_EDGE_ZERO_V1=0个百分点。不重复叠加存储预算；求解残差检查不放宽物理端点。

