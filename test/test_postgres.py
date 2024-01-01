import psycopg2
from psycopg2 import Error

import appplatform.startutil as startutil

def test_connect():
    try:
        connection = psycopg2.connect(user=startutil.appconfig.IParams['pg_test_user'],
                                      password=startutil.appconfig.IParams['pg_test_password'],
                                      host=startutil.appconfig.IParams['pg_test_host'],
                                      port=startutil.appconfig.IParams['pg_test_port'],
                                      database="icor")

        cursor = connection.cursor()
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")
        cursor.execute("SELECT * FROM icor.test1;")
        records = cursor.fetchall()
        print(records)

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

if __name__=='__main__':
    test_connect()
