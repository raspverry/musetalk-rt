# 프로젝트 상태

- 언어: [EN](PROJECT_STATUS.md) | **KO** | [JA](PROJECT_STATUS.ja.md)

## 프로젝트 정체성
MuseTalk-RT는 MuseTalk 파생 런타임 후보를 제품화하기 위한 검증/운영 근거 레이어입니다.

## What is done / What is left

### 완료
1. 웜 패스 정책 운영화
2. 라이프사이클 검증 체인 구축
3. 4개 핵심 단계 flagged 경로 provisional real-wired 확보
4. 30회 flagged 신뢰성 검증( fallback 0 / stage error 0 )
5. bursty/jittery 스트레스 검증에서 라이프사이클 안정성 유지
6. 안정/열화 구분 가능한 품질 텔레메트리 확보
7. 휴먼 QA 팩/스코어카드/의사결정 레이어 구축
8. 로컬 GUI 및 다국어 문서 제공

### 남음
1. 실제 리뷰어 점수 수집
2. 카나리 증거 패키지 완성
3. 모바일/네트워크 유사 조건의 지각 품질 근거 확보
4. 더 넓은 제품 준비성 게이트 정의

## Canary-ready 조건
- stable/bursty/jittery 대표 샘플에 대한 휴먼 점수 확보
- 의사결정 레이어가 임계치 기준 `GO_WARN_ONLY_CANARY` 달성
- 최근 flagged 신뢰성 지표에 회귀 없음
- 롤백 트리거 및 책임자 문서화

## Broader product-ready 조건
- 반복 세션 + 다수 평가자 기반 증거
- 평가자 간 일치도 확인
- 실제 배포 관점의 모니터링/롤백 운영성 검증
- flagged 범위 확장에 대한 이해관계자 승인
