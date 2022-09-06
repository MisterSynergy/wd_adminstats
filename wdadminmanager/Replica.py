from os.path import expanduser

from mysql.connector import FieldType, MySQLConnection
from mysql.connector.errors import ProgrammingError


#STRINGABLE_FIELDS = [ 'VAR_STRING', 'STRING' ]  # some are clearly missing here


class Replica:
    def __init__(self, database:str) -> None:
        self.replica = MySQLConnection(
            host=f'{database}.analytics.db.svc.wikimedia.cloud',
            database=f'{database}_p',
            option_files=f'{expanduser("~")}/replica.my.cnf'
        )
        self.cursor = self.replica.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.replica.close()

    @classmethod
    def query(cls, query:str, database:str='wikidatawiki') -> list[tuple]: #tuple[list[tuple], tuple[str], list[str]]:
        with cls(database) as db_cursor:
            try:
                db_cursor.execute(query)
            except ProgrammingError as exception:
                raise RuntimeError(f'Cannot query {query}') from exception
            else:
                result = db_cursor.fetchall()
#                column_names = db_cursor.column_names

#                columns_to_convert = []
#                for desc in db_cursor.description:
#                    if FieldType.get_info(desc[1]) not in STRINGABLE_FIELDS:
#                        continue

#                    columns_to_convert.append(desc[0])

        return result
