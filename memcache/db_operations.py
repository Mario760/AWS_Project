import mysql.connector

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
    # except:
    except mysql.connector.Error as e:
        # print("Error when connecting!")
        print(e)
        exit(1)

def get(key: str) -> list:
    """
    Search key in image table of database. If found, return value. If not found, return not found.
    """

    connect = db_connect()
    cursor = connect.cursor()

    query = ("SELECT * FROM image where `key` = %s")
    cursor.execute(query, (key,))
    result = cursor.fetchall()

    if len(result) == 0:
        return []
    
    else:
        return result[0][2]

def get_config() -> list:
    """
    Get Configuration details
    """

    connect = db_connect()
    cursor = connect.cursor()

    query = ("SELECT * FROM cache_config where `id` = (SELECT MAX(`id`) FROM cache_config)")
    cursor.execute(query)
    result = cursor.fetchall()

    if len(result) == 0:
        return []
    
    else:
        return result[0]

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

def put_memcache_stats(data: dict) -> str:
    """
    Put MemCache stats to database.
    """

    connect = db_connect()
    cursor = connect.cursor()
    
    query = ("UPDATE cache "
             "SET no_items = %s, total_size = %s, no_request = %s, miss_rate = %s, hit_rate = %s "
            )
    cursor.execute(query, (data['no_items'], data['total_size'], data['no_request'], data['miss_rate'], data['hit_rate']))
    connect.commit()

    return "Successfully updated memcache_stats."



def initialize_memcache_stats(data: dict) -> str:
    """
    Put MemCache stats to database.
    """

    connect = db_connect()
    cursor = connect.cursor()
    
    query = ("SELECT COUNT(*) from cache")
    cursor.execute(query)
    result = cursor.fetchall()
    
    if result[0][0] == 0:
        query = ("INSERT INTO cache "
                "(no_items, total_size, no_request, miss_rate, hit_rate) "
                "VALUES (%s, %s, %s, %s, %s)"
                )
        cursor.execute(query, (data['no_items'], data['total_size'], data['no_request'], data['miss_rate'], data['hit_rate']))

        connect.commit()
    
    else:
        query = ("UPDATE cache "
                 "SET no_items = %s, total_size = %s, no_request = %s, miss_rate = %s, hit_rate = %s"
                )
        cursor.execute(query, (0, 0, 0, 0, 0))

        connect.commit()

    return "Successfully inserted memcache_stats."

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



if __name__ == "__main__":
    key = input("Input Key:")
    print(get(key))
