# Local-File-Management

GPU 없이 CPU만으로 동작하는 로컬 문서 수집/인덱싱/검색 프로젝트입니다.

## 구성

- 수집기: 로컬 파일(`.txt`, `.md`, `.pdf`) + 웹 문서 URL
- 파서: 텍스트 추출/정제 (`pypdf`, `beautifulsoup4`)
- 인덱싱: `SQLite + FTS5`
- 검색 API: `FastAPI`
- 웹 UI: `Streamlit`
- 백그라운드 작업: `APScheduler`
- 테스트/품질: `pytest`, `ruff`, `mypy`, GitHub Actions CI

## 운영 안정성 개선 사항

- 입력 검증: 잘못된 로컬 경로/URL은 제어된 에러로 반환
- 검색 안정성: 잘못된 FTS 쿼리도 제어된 에러 응답
- 재인덱싱 정합성: 삭제된 로컬 파일 문서를 인덱스에서 자동 정리
- SQLite 운영 설정: `WAL`, `busy_timeout`, `synchronous=NORMAL`
- 수집 안전장치: 숨김 파일 제외 옵션, 최대 파일 크기 제한
- Streamlit 내구성: API 실패 시 앱 크래시 대신 오류 메시지 표시

## 환경 변수

- `LFM_DB_PATH` (기본값: `data/index.db`)
- `LFM_SCAN_PATH` (기본값: `.`)
- `LFM_MAX_FILE_SIZE_MB` (기본값: `20`)
- `LFM_EXCLUDE_HIDDEN` (기본값: `true`)

## 설치

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .[dev]
```

## CLI 사용

```bash
python main.py index <폴더경로> --db data/index.db
python main.py index-web "https://example.com" --db data/index.db
python main.py search "검색어" --db data/index.db --limit 20
```

## API 실행

```bash
uvicorn local_file_management.api.app:app --reload --app-dir src
```

엔드포인트:
- `GET /health`
- `POST /index` `{ "path": "." }`
- `POST /index/web` `{ "url": "https://example.com" }`
- `POST /search` `{ "query": "python", "limit": 20 }`

## Streamlit UI 실행

```bash
streamlit run app/streamlit_app.py
```

## 스케줄러 실행

```bash
python -m local_file_management.scheduler.worker
```

## 테스트/품질

```bash
pytest -q
ruff check .
mypy
```
