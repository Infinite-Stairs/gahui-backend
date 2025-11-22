--pgcrypto(암호화, 난수, UUID 생성 기능)확장을 활성화
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS plantar_result (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL    DEFAULT now(),

    l1_avg REAL NOT NULL,
    l2_avg REAL NOT NULL,
    l3_avg REAL NOT NULL,
    r1_avg REAL NOT NULL,
    r2_avg REAL NOT NULL,
    r3_avg REAL NOT NULL,

    left_sum_avg  REAL NOT NULL,
    right_sum_avg REAL NOT NULL,
    overall_avg   REAL NOT NULL,

    left_std  REAL,
    right_std REAL,

    left_pct  REAL NOT NULL CHECK (left_pct  BETWEEN 0 AND 100),
    right_pct REAL NOT NULL CHECK (right_pct BETWEEN 0 AND 100),
    cop_x_pct REAL NOT NULL CHECK (cop_x_pct BETWEEN 0 AND 100),
    cop_y_pct REAL NOT NULL CHECK (cop_y_pct BETWEEN 0 AND 100),

    cop_ok    SMALLINT NOT NULL CHECK (cop_ok IN (0,1))
);

--테이블 조회 속도를 높이기 위한 인덱스를 만드는 명령어
CREATE INDEX IF NOT EXISTS idx_plantar_result_created_at
  ON plantar_result (created_at DESC);
