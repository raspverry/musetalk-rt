# MuseTalk-RT (플래그 기반 비프로덕션 평가 툴킷)

- 언어: [English](README.md) | **한국어** | [日本語](README.ja.md)

## 이 프로젝트는 무엇인가요?
MuseTalk-RT는 MuseTalk 계열 세션 시작/연속성 품질을 검증하기 위한 **로컬 평가·QA 도구 모음**입니다.
프로덕션 UI/오케스트레이션이 아니라, 안정/교란 조건 비교, 라이프사이클 텔레메트리 검토, 휴먼 QA, 카나리 의사결정을 지원합니다.

## 현재 상태
- 플래그 기반 신뢰성/품질 스트레스 검증 체계가 마련됨
- 휴먼 QA 팩 + 의사결정 레이어 준비됨
- 다만 제품 준비성 주장은 아직 실험 단계(반복된 휴먼 점수/평가자 합의 필요)

## Korean quickstart
```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_pack.py   --stable-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_qv12_report.json   --bursty-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_stress_bursty_qv12_report.json   --jittery-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_stress_jittery_qv12_report.json

python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py   --qa-pack benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1.json   --scorecard benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_scorecard_template.json
```

## Typical workflow
1. [docs/GETTING_STARTED.ko.md](docs/GETTING_STARTED.ko.md)
2. [docs/ARCHITECTURE.ko.md](docs/ARCHITECTURE.ko.md)
3. [docs/QA_WORKFLOW.ko.md](docs/QA_WORKFLOW.ko.md)
4. [docs/REPORTS_AND_DECISIONS.ko.md](docs/REPORTS_AND_DECISIONS.ko.md)

## 로컬 GUI
```bash
pip install streamlit
streamlit run app/qa_dashboard.py
```
