# 아키텍처 (플래그 기반 검증 스택)

- 언어: [EN](ARCHITECTURE.md) | **KO** | [JA](ARCHITECTURE.ja.md)

## 구성요소
- harness, baseline runner, approx fixture, reliability/quality/human-QA/decision 스크립트
- 결과는 `reports/`에 저장

## Real vs Proxy
- 일부 라이프사이클 단계는 플래그 하에서 real-wired 관측
- 프레임 생성/케이던스는 fixture 기반 근사
- fallback 가시성은 보고서에 유지

