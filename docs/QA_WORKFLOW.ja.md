# QAワークフロー

- 言語: [EN](QA_WORKFLOW.md) | [KO](QA_WORKFLOW.ko.md) | **JA**

1) stable / bursty / jittery レポートを準備
2) QAパック生成
3) best/median/worst を目視レビュー
4) スコアカード入力
5) 判断スクリプト実行

```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_pack.py
python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py
```

