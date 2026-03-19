# Local-File-Management

GPU 없이 CPU만으로 동작하는 로컬 문서 수집/인덱싱/검색 프로젝트

## 구성

- 수집기: 로컬 파일(`.txt`, `.md`, `.pdf`) + 웹 문서 URL
- 파서: 텍스트 추출/정제 (`pypdf`, `beautifulsoup4`)
- 인덱싱: `SQLite + FTS5`
- 검색 API: `FastAPI`
- 웹 UI: `Streamlit`
- 백그라운드 작업: `APScheduler`
- 테스트/품질: `pytest`, `ruff`, `mypy`, GitHub Actions CI

## 신뢰성 동작

- 잘못된 로컬 경로/URL은 즉시 검증 후 제어된 에러로 반환합니다.
- 잘못된 FTS 쿼리는 API/CLI에서 제어된 에러로 반환합니다.
- 로컬 재인덱싱 시 삭제된 파일 문서는 인덱스에서 자동 정리됩니다.

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
