import mysql.connector

import time

DUMMY_USER = 0
HOST_ENDPOINT = 'ece1779-project2-db0.c5m47mkaqikn.us-east-1.rds.amazonaws.com'

def db_connect():

    config = {
        'user': 'Joey',
        'password': 'joey0101',
        'host': HOST_ENDPOINT,
        'database': 'image_db'
    }

    try:
        c = mysql.connector.connect(**config)
        return c
    except:
        print("Error when connecting!")
        exit(1)

def delete_all_pairs():
    return initialize_images()


def get(key: str) -> str:
    """
    Search key in image table of database. If found, return value. If not found, return not found.
    """

    connect = db_connect()
    cursor = connect.cursor()

    query = ("SELECT * FROM image where `key` = %s")
    cursor.execute(query, (key,))
    result = cursor.fetchall()

    if len(result) == 0:
        return "Unknown Key!"
    
    else:
        return result[0][2]

def remove(key: str) -> str:
    """
    Remove key-value pair in image table of database using key. Return result.
    """

    connect = db_connect()
    cursor = connect.cursor()
    
    query = ("DELETE FROM image where `key` = %s")
    cursor.execute(query, (key,))
    connect.commit()

    return "Successfully deleted key-value pair with key {0} to DB.".format(key)

def put(key: str, value: str) -> str:
    """
    Put key-value pair in image table of database. Return result.
    """

    connect = db_connect()
    cursor = connect.cursor()
    
    query = ("INSERT INTO image "
             "(`key`, value) "
             "VALUES (%s, %s)"
            )
    cursor.execute(query, (key, value))
    connect.commit()

    return "Successfully added key-value pair {0}-{1} to DB.".format(key, value)

def put_memcache_config(capacity: str, policy: str) -> str:
    """
    Store memcache configurations into database
    """

    connect = db_connect()
    cursor = connect.cursor()
    
    query = ("SELECT COUNT(*) from cache_config")
    cursor.execute(query)
    result = cursor.fetchall()

    if result[0][0] == 0:
        query = ("INSERT INTO cache_config "
                "(capacity, policy) "
                "VALUES (%s, %s)"
                )
        cursor.execute(query, (capacity, policy))
        connect.commit()
    else:
        query = ("UPDATE cache_config "
                 "SET capacity = %s, policy = %s"
                )
        cursor.execute(query, (capacity, policy))

        connect.commit()


    return "Successfully added capacity {0} and policy {1} configurations to DB.".format(capacity, policy)

def get_memcache_stat() -> dict:
    """
    Get memcache_stats of previous five minutes from database
    """

    connect = db_connect()
    cursor = connect.cursor()
    
    query = ("SELECT * FROM cache where `id` = (SELECT MAX(`id`) FROM cache)")
    cursor.execute(query)
    result = cursor.fetchall()

    if len(result) == 0:
        return "No Data"
    else:
        res = {}
        for row in result:
            res['no_items'] = row[1]
            res['total_size'] = row[2] / 1000000
            res['no_request'] = row[3]
            res['miss_rate'] = row[4] / row[3] * 100 if row[3] != 0 else 0
            res['hit_rate'] = row[5] / row[3] * 100 if row[3] != 0 else 0
        
        
        if not (res['no_items'] or res['total_size'] or res['no_request'] or res['miss_rate'] or res['hit_rate']):
            time.sleep(1)
            res = {}
            connect = db_connect()
            cursor2 = connect.cursor()
            cursor2.execute(query)
            result2 = cursor2.fetchall()
            for row in result2:
                res['no_items'] = row[1]
                res['total_size'] = row[2] / 1000000
                res['no_request'] = row[3]
                res['miss_rate'] = row[4] / row[3] * 100 if row[3] != 0 else 0
                res['hit_rate'] = row[5] / row[3] * 100 if row[3] != 0 else 0
            return res

        return res


def display_keys() -> list:

    connect = db_connect()
    cursor = connect.cursor()

    query = ("SELECT * FROM image")
    cursor.execute(query)
    result = cursor.fetchall()
    
    if len(result) == 0:
        return []
    
    else:
        res = []
        for row in result:
            res.append([row[1], row[2]])
        return res

def initialize_images():
    connect = db_connect()
    cursor = connect.cursor()

    query = ("SELECT COUNT(*) from image")
    cursor.execute(query)
    result = cursor.fetchall()

    if result[0][0] != 0:
        query = ("DELETE FROM image")
        cursor.execute(query)
        connect.commit()
    
    return print("Successfully cleaned {0} entries in table `image`.".format(result[0][0]))


if __name__ == "__main__":
    # key = input("Input Key:")
    # print(remove(key))
    print(db_connect())
