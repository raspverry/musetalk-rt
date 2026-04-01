# はじめに

- 言語: [EN](GETTING_STARTED.md) | [KO](GETTING_STARTED.ko.md) | **JA**

## スコープ
本リポジトリは**フラグ付き非本番**の検証用途です。

## 10分オンボーディング
1. Python 3.10+
2. `benchmarks/baseline/reports` の既存成果物を確認
3. QAパック/判断スクリプトを実行

```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_pack.py
python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py
```

