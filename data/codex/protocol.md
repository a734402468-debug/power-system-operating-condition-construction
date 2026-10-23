# GPT配置适用性补充 v1

定位：官方Codex接入下的GPT配置适用性，不宣称与历史chat/completions同参数或同系统指令。

## 任务与顺序

主运行：T1、T2、T3、T4、V1、V2、V3、V4、L1、L2、L3、L4。
然后：T2-r2、T2-r3、V3-r2、V3-r3、L3-r2、L3-r3。
共18条轨迹；代表任务r1就是主运行，不能重复算作新任务。每条最多一次原公共诊断修订；最多36次正式CLI启动。两次合成探针单列。

每题首次请求取20261017正式批次归档request.json的messages，逐字保留内容及顺序；外层旧model、temperature等元数据仅为来源，不发送到Codex。以`<original_message role="…">`分隔后送入exec stdin，角色优先级无法原样映射，明确披露。无额外案例、正确规格、答案、候选或评分反馈。修订沿用20261017/18公共诊断；新会话包含原messages、自身回答及允许反馈，不resume/fork。

## 调用配置与隔离

- 官方CLI 0.163.0；现有ChatGPT登录，未读取认证正文或验证Pro余额。
- requested_model=gpt-6.1-sol，model_reasoning_effort=medium。若事件未提供返回模型/快照，记录unknown；不采信自述身份。
- 每次全新临时目录、ephemeral会话、ignore-user-config、ignore-rules；不传output-schema；普通最终输出交原解析器。
- features.shell_tool、搜索、MCP配置、插件、memory、multi_agent等禁用项详见每次command.json及codex_adapter.py。内置skills须以SKILL.md文件路径禁用，本机静态检查已验证；目录路径设置曾未生效，保留准备记录。
- sandbox read-only不是隔离证明。合成探针主动要求使用可用工具，实际未见调用；正式事件一旦出现工具项，停止整批、不重发。服务器完整工具schema不能由标准exec日志穷尽证明，保留这一可观察性限制。
- 外部进程总截止180秒。没有把JSONL事件空闲称作60秒网络空闲；不伪造temperature、top_p、4096输出上限或enable_thinking对应关系。
- 用户API Key环境变量从子进程环境移除；认证仍由官方CLI处理。所有配置仅本轮命令参数，不修改全局文件。
- CLI启动数、可见session/turn、工具事件、重连和usage分别记录，内部底层请求计数unknown。WebSocket到HTTPS是官方客户端传输回退，不是模型/服务商切换。控制端不自动重启失败尝试。

官方配置依据：<https://developers.openai.com/codex/config-reference/>（本轮实际打开，重定向至ChatGPT Learn）；最终可用字段以本机help/features和探针记录为准。

## 下游与物理流程

独立downstream目录保存20261017冻结哈希匹配的42个Python依赖；当前两处差异用已归档before_edit恢复到本轮目录，未覆盖源荷现行代码。补齐一个既有动态加载NJ helper，哈希与其历史freeze一致。三类代表T2/V3/L3已通过归档数学问题展开相等检查，不运行历史目标求解或PF。

隔离正确规格只用于评价端。原自动评分与已登记有限认证保留，新的歧义标未决，不能由研究GPT主观自评放行。生成规格通过后最多一次物理候选；不使用源荷校正、不改目标、权限或阈值。

物理复用沿用完整P/Q、基准、控制/潮流配置、响应、权限、阶段及既有恢复匹配。无法匹配则使用旧Session基准—候选—恢复。内部正常预算54AC、异常恢复预留6AC；最多18候选，不为耗尽预算追加运行。源工程及NJ/CG研究副本之外不写入。恢复或状态绑定失败停止后续物理操作。

源荷和前端证据只做归档提取，新增调用/AC为0。S-T/S-V/S-L不与12题合并成功率。B/P只保留本批紧凑表达观察。

## 停止与归档

普通合同/语义/数值/物理失败保留并继续。模型不可用、认证额度、协议工具事件、证据损坏、共同执行或恢复故障停止受影响部分。沿用旧调度器连续三次调用失败暂停模型的保护；未发送项保持18条清单，不计模型理解错误。历史成绩不回写。

`freeze.json`、`downstream_version_check.json`、`dynamic_dependency_provenance.json`记录版本。`case_results`主表12行，`repeatability_results`9行，其中3个r1重合；所有正式逐轨迹在`all_trajectories.json`。用量不等于费用，机器时间不等于人工时间。
