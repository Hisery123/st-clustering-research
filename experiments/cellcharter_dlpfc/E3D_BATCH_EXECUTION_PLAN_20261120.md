# E3d剩余46配置：一次性事前审核与批量执行计划（2026-11-20）

## 冻结目标与真实状态

- 原实验协议：`E3D_AUTOK_FROZEN_PROTOCOL_20261120.md`。总计**12张切片×4个固定累计尺度(10/15/20/25D) = 48个配置**；每配置CPU、AutoK候选K2..10、内部K1..11、每K显式播种5次（计划55次GMM），实验特征和上游数据锁定，选K完全不用人工层标签。
- 已由用户Windows真实终端报告`151509/15D`与`151509/25D`分别`E3D_FIXED_TASK_COMPLETE`，两个配置的AutoK选K均为3；15D已独立审核产物，25D仅运行成功尚未做独立产物审核。按照**用户最新执行优先策略**，不再单独审核25D作为继续门槛。
- 本批新增任务至多**46配置/2530次GMM拟合（计划）**；已有2项绝不重跑或覆盖。**用户尚未运行批量任务，不能称46项已完成。**

## 执行器预先验收

- [已完成／作者侧静态检查] GitHub版本`e3d_autok_batch_runner_v1.py`，SHA256 **`c9fc65275638a1627a1c836198e8804ecfa866938377448e0de40346d9d01191`**；Git blob SHA1 `e3dffacb958f80af047bc9bea986440bc40a3197`。采用标准库，无新依赖。
- [已完成／隔离模拟] 在助手容器的模拟文件夹，构造48任务、2个历史完成目录、46个待运行目录，读取计划显示`completed=2 pending=46`；验证已存在但无manifest的输出会被标记`blocked`，且只读规划不创建会话目录。**此为测试桩，不是用户真实数据训练，不代替Windows验证。**
- [尚未执行] 用户需将脚本从GitHub下载至`D:\paper\CellCharter_reproduction\e3d_autok_batch_runner_v1.py`并SHA256校验；运行**不带--run**的单次只读执行计划，确认实际`completed=2 pending=46 blocked=0`；然后运行`--run`一次性自动执行剩余任务。无需每完成一片再手工审计。

## 安全边界与断点

1. runner只做**任务编排**，每次仍通过用户已在Windows验收的`e3d_autok_single_config_v1.py`运行冻结算法；启动前和每项启动前验证单任务脚本SHA256 `24f500a953e73055d44bfbe3b68e2301f3aeab7e9046035fe31bc2ca81ed8da2`。参数不因选择K或性能值而更改。
2. **轻量防覆盖**：检查已有目录的manifest协议、参数、预期文件及summary状态；已有完成项只跳过，不对每配置进行科研产物重审；遇到疑似运行中、缺失或不兼容输出，停止并保留现场。
3. 记录：`results/e3d_autok_batch_sessions_v1/<UTC>_<PID>/session_status.json`逐项原子更新；每项完整stdout/stderr写入`task_NN_<slice>_<dim>D.log`。每项状态为completed/skipped_existing/failed等；不会静默重试失败、删除旧目录或覆盖输出。会话目录使用全新唯一名称。
4. 单一配置失败：保留输出和完整日志，**跳过该样本余下配置后继续其他样本**。同一阶段连续两个不同样本失败、环境/源文件不符、目录冲突、磁盘写入等疑似全局问题则停止并保留会话记录；不会冒充成功。
5. 会话互斥锁：`results/e3d_autok_batch_sessions_v1/_ACTIVE_BATCH.lock`防止同时运行两个批处理；异常强杀若遗留锁，由用户提供现场后人工判断，不自行删除/自动重启。
6. 任意时候只允许用户Windows自己启动，不默认远程执行、Codex或者改变site-packages；正式执行前的只读规划是**阶段开始前的一次性检查**，不是中途科研审稿。

## 用户本机执行顺序（每回合只给一条命令）

1. 下载Runner并校验SHA256，不覆盖本地同名未知文件；可以在同一PowerShell命令中立即执行只读计划（仍不训练）。必须收到实际日志确认`blocked=0`、历史两项跳过、剩余数量合理。
2. 用户独立执行该runner`--run`，程序持续推进余46配置，保留真实进度日志。
3. **整个阶段结束后**统一运行全局产物/完整性审核；整理所有失败和K选择、性能，连同原始CSV/JSON与协议交Claude集中方法学审核。不得因中途单个K3/K4差异或新想法插入实验。

历史`PROJECT_STATE.md`和旧handoff里的逐项即时审计建议已被`EXECUTION_FIRST_CLAUDE_FINAL_REVIEW_DECISION_20261120.md`覆盖。
