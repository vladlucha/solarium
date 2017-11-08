from django.db import connection
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salarium.settings")


def init():
    cursor = connection.cursor()
    tables = connection.introspection.table_names()

    for table in tables:
        print("Fixing table: %s" % table)
        sql = "ALTER TABLE %s CONVERT TO CHARACTER SET utf8;" % table
        cursor.execute(sql)
        print("Table %s set to utf8" % table)

    print("DONE!")

init()
