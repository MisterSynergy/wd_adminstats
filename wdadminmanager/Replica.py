from os.path import expanduser
from typing import Any

import mariadb


class Replica:
    def __init__(self, database:str) -> None:
        self.replica = mariadb.connect(
            host=f'{database}.analytics.db.svc.wikimedia.cloud',
            database=f'{database}_p',
            default_file=f'{expanduser("~")}/replica.my.cnf'
        )
        self.cursor = self.replica.cursor(dictionary=True)

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.replica.close()

    @classmethod
    def query(cls, query:str, database:str='wikidatawiki') -> list[dict[str, Any]]:
        with cls(database) as db_cursor:
            try:
                db_cursor.execute(query)
            except mariadb.ProgrammingError as exception:
                raise RuntimeError(f'Cannot query {query}') from exception

            result = db_cursor.fetchall()

        return result
