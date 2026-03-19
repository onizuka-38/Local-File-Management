from apscheduler.schedulers.blocking import BlockingScheduler

from local_file_management.config import settings
from local_file_management.indexer.sqlite_indexer import get_connection
from local_file_management.pipeline import index_local_path


def scheduled_index() -> None:
    conn = get_connection(settings.db_path)
    try:
        index_local_path(conn, settings.scan_path)
    finally:
        conn.close()


def main() -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_index, "interval", minutes=30, max_instances=1, coalesce=True)
    scheduler.start()


if __name__ == "__main__":
    main()
