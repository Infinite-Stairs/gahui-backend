import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Any, Dict, List

DB_DSN = os.getenv("DB_DSN", "postgresql://plantar_min_db_user:HFRT1QPoIxlpErmhrfRTKOwS4XVjOS9P@dpg-d4i358ggjchc73dk5de0-a.oregon-postgres.render.com/plantar_min_db?sslmode=require")

@contextmanager
def get_conn():
    conn = psycopg2.connect(DB_DSN)
    try:
        yield conn
    finally:
        conn.close()
#테이블 관리 함수
def init_schema() -> None:
    ddl = """
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    CREATE TABLE IF NOT EXISTS plantar_result (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

        l1_avg REAL NOT NULL, l2_avg REAL NOT NULL, l3_avg REAL NOT NULL,
        r1_avg REAL NOT NULL, r2_avg REAL NOT NULL, r3_avg REAL NOT NULL,

        left_sum_avg REAL NOT NULL,
        right_sum_avg REAL NOT NULL,
        overall_avg REAL NOT NULL,

        left_std REAL,
        right_std REAL,

        left_pct  REAL NOT NULL CHECK (left_pct  BETWEEN 0 AND 100),
        right_pct REAL NOT NULL CHECK (right_pct BETWEEN 0 AND 100),
        cop_x_pct REAL NOT NULL CHECK (cop_x_pct BETWEEN 0 AND 100),
        cop_y_pct REAL NOT NULL CHECK (cop_y_pct BETWEEN 0 AND 100),
        cop_ok    SMALLINT NOT NULL CHECK (cop_ok IN (0,1))
    );
    CREATE INDEX IF NOT EXISTS idx_plantar_result_created_at
      ON plantar_result (created_at DESC);
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
#데이터 삽입 함수
def insert_result(row: Dict[str, Any]) -> Dict[str, str]:
    sql = """
    INSERT INTO plantar_result (
      l1_avg,l2_avg,l3_avg,r1_avg,r2_avg,r3_avg,
      left_sum_avg,right_sum_avg,overall_avg,
      left_std,right_std,
      left_pct,right_pct,cop_x_pct,cop_y_pct,cop_ok
    ) VALUES (
      %(l1_avg)s,%(l2_avg)s,%(l3_avg)s,%(r1_avg)s,%(r2_avg)s,%(r3_avg)s,
      %(left_sum_avg)s,%(right_sum_avg)s,%(overall_avg)s,
      %(left_std)s,%(right_std)s,
      %(left_pct)s,%(right_pct)s,%(cop_x_pct)s,%(cop_y_pct)s,%(cop_ok)s
    )
    RETURNING id, created_at
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, row)
            out = cur.fetchone()
        conn.commit()
    return {"id": str(out["id"]), "created_at": out["created_at"].isoformat()}
#최근 데이터 조회 함수
def fetch_latest(n: int = 5) -> List[Dict[str, Any]]:
    sql = """
    SELECT id, created_at,
           l1_avg,l2_avg,l3_avg,r1_avg,r2_avg,r3_avg,
           left_sum_avg,right_sum_avg,overall_avg,
           left_std,right_std,
           left_pct,right_pct,cop_x_pct,cop_y_pct,cop_ok
    FROM plantar_result
    ORDER BY created_at DESC
    LIMIT %s
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (n,))
            return cur.fetchall()
