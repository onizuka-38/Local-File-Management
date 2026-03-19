# Local-File-Management

GPU 없이 CPU만으로 동작하는 로컬 문서 수집/인덱싱/검색 프로젝트입니다.

## 구성

- 수집기: 로컬 파일(`.txt`, `.md`, `.pdf`) + 웹 문서 수집 코드
- 파서: 텍스트 추출/정제 (`pypdf`, `beautifulsoup4`)
- 인덱싱: `SQLite + FTS5`
- 검색 API: `FastAPI`
- 웹 UI: `Streamlit`
- 백그라운드 작업: `APScheduler`
- 테스트/품질: `pytest`, `ruff`, `mypy`, GitHub Actions CI

## 설치

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .[dev]
```

## CLI 사용

```bash
python main.py index <폴더경로> --db data/index.db
python main.py search "검색어" --db data/index.db --limit 20
```

## API 실행

```bash
uvicorn local_file_management.api.app:app --reload --app-dir src
```

엔드포인트:
- `GET /health`
- `POST /index` `{ "path": "." }`
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
