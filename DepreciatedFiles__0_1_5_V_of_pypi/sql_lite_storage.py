"""SQL_Lite Implementation of storage interface"""
import asyncio
import sqlite3
from typing import List, Dict

from src.Interfaces.message_interface import MessageInterface
from src.Interfaces.storage_interface import StorageInterface
from Custom_logger import logger


class SQL_Lite_Storage(StorageInterface):
    """Async-safe SQLite storage with queue-based single writer
    ## Lifecycle
        - Storage is created once at application startup.
        - A shared asyncio.Queue is injected explicitly.
        - Writer task is started lazily on first enqueue.
        - Shutdown is handled via `close_db()`.
    """

    def __init__(self, queue: asyncio.Queue, db_path: str = "tweakio.db"):
        super().__init__(queue)
        self.db_path = db_path
        self.conn = None
        self._writer_task = None
        self._closed = False
        self.init_db()

    # ---------- lifecycle ----------

    def init_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA busy_timeout=3000;")
            self.create_table()
            logger.info(f"SQLite initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"DB init failed: {e}", exc_info=True)
            raise

    def create_table(self):
        query = """
                CREATE TABLE IF NOT EXISTS messages
                (
                    data_id
                    TEXT
                    PRIMARY
                    KEY,
                    chat
                    TEXT,
                    community
                    TEXT,
                    jid
                    TEXT,
                    message
                    TEXT,
                    sender
                    TEXT,
                    systime
                    TEXT,
                    direction
                    TEXT,
                    data_type
                    TEXT
                ); \
                """
        self.conn.execute(query)
        self.conn.commit()

    def start_writer(self):
        if self._writer_task is None or self._writer_task.done():
            self._writer_task = asyncio.create_task(self._writer_loop())

    # ---------- public API ----------

    async def enqueue_insert(self, msgs: List[MessageInterface]):
        if not msgs or self._closed:
            return
        self.start_writer()
        await self.queue.put(msgs)


    def check_message_if_exists(self, msg_id: str) -> bool:
        try:
            cur = self.conn.execute(
                "SELECT 1 FROM messages WHERE data_id = ?", (msg_id,)
            )
            return cur.fetchone() is not None
        except Exception as e:
            logger.error(f"Exist check failed: {e}", exc_info=True)
            return False

    def get_all_messages(self) -> List[Dict]:
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.execute("SELECT * FROM messages")
        return [dict(r) for r in cur.fetchall()]

    async def close_db(self):
        self._closed = True

        if self._writer_task and not self._writer_task.done():
            self._writer_task.cancel()
            try:
                await self._writer_task
            except asyncio.CancelledError:
                pass

        if not self.queue.empty():
            await self.queue.join()

        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed")

    # ---------- writer internals ----------

    async def _writer_loop(self):
        while not self._closed:
            try:
                msgs = await self.queue.get()
                try:
                    await self._insert_batch_internally(msgs)
                finally:
                    self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[WriterLoop] {e}", exc_info=True)

    async def _insert_batch_internally(self, msgs: List[MessageInterface]):
        if not msgs:
            return

        rows = await asyncio.gather(*(m.GetTraceObj() for m in msgs))
        loop = asyncio.get_running_loop()

        await loop.run_in_executor(
            None,
            self._sync_insert_rows,
            rows,
            msgs,
        )

    # ---------- sync DB work (threaded) ----------

    def _sync_insert_rows(self, rows, msgs):
        try:
            q = """
                INSERT
                OR IGNORE INTO messages
            (data_id, chat, community, jid, message, sender, systime, direction, data_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) \
                """
            self.conn.executemany(q, rows)
            self.conn.commit()

            ids = [m.data_id for m in msgs]
            if not ids:
                return

            ph = ",".join("?" * len(ids))
            cur = self.conn.execute(
                f"SELECT data_id FROM messages WHERE data_id IN ({ph})", ids
            )
            inserted = {r[0] for r in cur.fetchall()}

            for m in msgs:
                if m.data_id not in inserted:
                    m.Failed = True

        except Exception as e:
            logger.error(f"[SQLite Sync Insert] {e}", exc_info=True)
