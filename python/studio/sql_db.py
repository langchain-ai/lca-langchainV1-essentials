"""Minimal local SQLDatabase — drop-in for the subset of
langchain_community.utilities.SQLDatabase used in this course
(from_uri, run, get_usable_table_names, get_table_info, dialect).

langchain-community is being sunset (see
https://github.com/langchain-ai/langchain-community/issues/674) and even importing it
now raises a DeprecationWarning. This avoids the dependency entirely using plain
SQLAlchemy, which the original implementation wraps anyway.
"""

from __future__ import annotations

from sqlalchemy import MetaData, create_engine, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql.sqltypes import NullType


class SQLDatabase:
    def __init__(
        self,
        engine: Engine,
        sample_rows_in_table_info: int = 3,
        max_string_length: int = 300,
    ):
        self._engine = engine
        self._sample_rows_in_table_info = sample_rows_in_table_info
        self._max_string_length = max_string_length
        self._metadata = MetaData()
        self._metadata.reflect(bind=self._engine)

    @classmethod
    def from_uri(cls, database_uri: str, **kwargs) -> "SQLDatabase":
        return cls(create_engine(database_uri), **kwargs)

    @property
    def dialect(self) -> str:
        return self._engine.dialect.name

    def get_usable_table_names(self):
        return sorted(t.name for t in self._metadata.sorted_tables)

    def _get_sample_rows(self, table) -> str:
        command = select(table).limit(self._sample_rows_in_table_info)
        columns_str = "\t".join(col.name for col in table.columns)
        try:
            with self._engine.connect() as conn:
                rows = [[str(v)[:100] for v in row] for row in conn.execute(command)]
            sample_rows_str = "\n".join("\t".join(row) for row in rows)
        except ProgrammingError:
            sample_rows_str = ""
        return (
            f"{self._sample_rows_in_table_info} rows from {table.name} table:\n"
            f"{columns_str}\n"
            f"{sample_rows_str}"
        )

    def get_table_info(self, table_names=None) -> str:
        meta_tables = [
            tbl
            for tbl in self._metadata.sorted_tables
            if (table_names is None or tbl.name in table_names)
            and not (self.dialect == "sqlite" and tbl.name.startswith("sqlite_"))
        ]
        tables = []
        for table in meta_tables:
            for col in list(table.columns):
                if type(col.type) is NullType:
                    table._columns.remove(col)
            create_table = str(CreateTable(table).compile(self._engine)).rstrip()
            sample_rows = self._get_sample_rows(table)
            tables.append(f"{create_table}\n\n/*\n{sample_rows}\n*/")
        tables.sort()
        return "\n\n".join(tables)

    def run(self, command: str, fetch: str = "all") -> str:
        with self._engine.begin() as conn:
            cursor = conn.execute(text(command))
            if not cursor.returns_rows:
                return ""
            rows = cursor.fetchone() if fetch == "one" else cursor.fetchall()
            rows = [rows] if fetch == "one" and rows is not None else (rows or [])

        def trunc(v):
            if isinstance(v, str) and len(v) > self._max_string_length:
                return v[: self._max_string_length - 3] + "..."
            return v

        result = [tuple(trunc(v) for v in row) for row in rows]
        return str(result) if result else ""
