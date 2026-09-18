# Pilot B0 预注册（2026-09-18，在看到任何 n=300 结果之前写）

数据：Banking77 test，随机抽 n=300（seed=0），77 类。
方法：Jev（choice，77 类）；gpt-5.4-nano（JSON 输出 + 自报置信度）；gpt-5.6-terra（同样提示）；
离线级联：Jev 置信度 < t 时改用 Terra 的答案（t 扫 0–1）；对照级联 nano→Terra。
指标：准确率（附 95% bootstrap CI）、中位 / p95 延迟、每次调用成本、置信度区分对错的 AUROC。

放弃（KILL）条件——同时满足则判定"Jev 在工作流里没有独特价值"：
  K1. nano 准确率 ≥ Jev − 3 个百分点，且 nano 中位延迟 ≤ 2 × Jev 中位延迟；
  K2. Jev→Terra 级联在"Terra 调用率 ≤ 50%"约束下的最佳准确率，不比 nano→Terra 级联高（差 < 2 个百分点）。
继续（GO）条件：Jev→Terra 级联在调用 Terra ≤ 50% 时，准确率达到 Terra 单用 −1 个百分点以内，并且比 nano→Terra 级联好 ≥ 2 个百分点。
介于两者之间 = 模糊，只报告，不据此扩展实验。
预算：LLM 侧 ≤ $2。
