# Pilot B1 预注册（2026-09-18 12:30 PDT，写于任何 B1 模型调用之前）

## 要检验的假设
H1：在零样本路由场景里（没有训练数据），用 Jev 的置信度决定哪些样本交给大模型，
比用小 LLM 自报的置信度更省：要达到同样的准确率，交给大模型的样本更少。

来源：B0（Banking77）中的事后观察——Jev→Terra 让 25% 样本走 Terra 就追平 Terra，
nano→Terra 需要 44%。B1 在一个独立数据集上检验它，指标和判定规则都提前固定。

## 数据
- CLINC150（clinc/oos-eval, data_full.json）。候选池 = test（4500，150 类）+ oos_test（1000，标签 `oos`）。
- 用 `random.Random(1)` 从候选池无放回抽 **n = 200**。标签空间 = 150 个意图 + `oos`（共 151 个）。
- 不使用任何训练数据（零样本）。Banking77 的结果和提示词不针对 CLINC 再调。

## 方法（每条样本都跑三种）
- **Jev**：choice 问题，151 个选项，criteria = 标签名把下划线换成空格；`oos` 的描述写成
  "out of scope: the request does not match any other intent"。置信度 = `providerMetadata.typesafe.confidence`。
- **nano**（openai/gpt-5.4-nano-2026-03-17）和 **Terra**（openai/gpt-5.6-terra）：与 B0 相同的 JSON 提示词，
  只把领域词从 "bank customer message" 换成 "virtual assistant user request"；置信度 = 模型自报的 0–1 值。
- 解析失败或调用失败（重试后）= 答错，置信度记 0（一定会交给大模型）。

## 主指标（唯一用来判定的指标）
设 A_T = Terra 单用的准确率，目标准确率 = A_T − 0.01。
对第一级 f ∈ {jev, nano}：级联规则为"置信度 < t 就用 Terra 的答案"，t 在所有出现过的置信度值和 {0, 1.01} 上扫描；
R_f = 使级联准确率 ≥ 目标的**最小 Terra 调用率**（任何 t 都达不到时，R_f = 1）。
**Δ = R_nano − R_jev**（正数表示 Jev 更省）。
置信区间：按样本做 2000 次 bootstrap（seed 0），每次重抽样都重新计算 A_T、R_jev、R_nano 和 Δ；报告 95% 百分位区间。

## 判定规则
- **继续（GO）**：Δ ≥ 0.10 且 Δ 的 95% 区间下界 > 0。
- **放弃（KILL）**：Δ ≤ 0，或 Δ 的 95% 区间上界 < 0.05。
- 其他情况 = **模糊**：不扩大实验，把 H1 记为"未证实"。

## 次要指标（只报告，不参与判定）
1. 置信度 AUROC：Jev vs nano vs Terra，配对 bootstrap 求差值的区间。
2. 交叉拟合版 Δ：样本随机分成两半（seed 2），在一半上选 t，到另一半上评估，两个方向取平均。用来检查主指标里"在测试集上挑阈值"的乐观偏差。
3. 各方法的准确率、中位 / p95 延迟、每次调用成本。
4. `oos` 这一类单独的召回率。

## 已知局限（预先声明）
- 主指标在测试集上挑阈值，偏乐观；但对 Jev 和 nano 是对称的，偏差方向相同。次要指标 2 用来检查。
- n=200 时，Δ 的区间可能很宽。所以设了"模糊"这一档，不会因为宽区间就判继续。
- LLM 的置信度是自报的（Lightning 上 nano 不支持 logprobs），可能低估 LLM 置信度的上限。这点会写进结论的适用范围。
- Jev 走 Vercel 免费档，限流约每分钟 1–2 次；限流失败的样本会重试到成功，不会当作答错丢弃。

## 预算
LLM 侧 ≤ $2（Lightning `ickma2311-org/inference`）；Jev 每次约 $0.0001。
