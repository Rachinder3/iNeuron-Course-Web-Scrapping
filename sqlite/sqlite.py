import sqlite3
from logger.logger import Logger


class sqlite:
    __log_obj = Logger("logs\\log.log")

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

        # create cursor
        self.cur = self.conn.cursor()

    def create_table(self, query):
        try:
            self.cur.execute(query)
            self.conn.commit()
            sqlite.__log_obj.add_log("create table function successful")
        except Exception as e:
            sqlite.__log_obj.add_log("create table function successful")
            sqlite.__log_obj.add_log(str(e))

    def execute_query_with_commit(self, query):
        try:

            self.cur.execute(query) # execute the query
            self.conn.commit()  # commit
            sqlite.__log_obj.add_log("execute query with commit successful")

        except Exception as e:
            sqlite.__log_obj.add_log("problem in execute query with commit")
            sqlite.__log_obj.add_log(str(e))

    def execute_query_without_commit(self, query):
        try:
            return self.cur.execute(query)
        except Exception as e:
            sqlite.__log_obj.add_log("problem in execute_query_without_commit")
            sqlite.__log_obj.add_log(str(e))
