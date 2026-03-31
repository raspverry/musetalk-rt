# QA 워크플로

- 언어: [EN](QA_WORKFLOW.md) | **KO** | [JA](QA_WORKFLOW.ja.md)

1) stable/bursty/jittery 보고서 준비
2) QA 팩 생성
3) best/median/worst 샘플 검토
4) 점수 입력
5) 의사결정 평가 실행

```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_pack.py
python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py
```

