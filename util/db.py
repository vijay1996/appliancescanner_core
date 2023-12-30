import psycopg2 as db
import datetime

def executeQuery(query):
    try:
        conn = db.connect("dbname='ApplianceScanner' user='Vijay' host='localhost' password='vbr1996'")
        print("[" + datetime.datetime.now() + "]" + "connected successfully...")
        print(conn.cursor().execute(query))
        conn.close()
        print("[" + datetime.datetime.now() + "]" + "query processed...")
    except:
        print("[" + datetime.datetime.now() + "]" + "some error occured...")