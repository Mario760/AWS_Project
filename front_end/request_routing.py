import hashlib

def md5_hash(key: str):
    return hashlib.md5(key.encode('utf-8')).hexdigest()

def request_route(pool_count: int, key: str) -> int:
    md5_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
    partition_16 = -1

    if (len(md5_hash) == 31):
        partition_16 = 0
    elif (str(md5_hash[0]).isdigit()):
        partition_16 = int(md5_hash[0])
    elif (md5_hash[0] == 'A' or md5_hash[0] == 'a'):
        partition_16 = 10
    elif (md5_hash[0] == 'B' or md5_hash[0] == 'b'):
        partition_16 = 11
    elif (md5_hash[0] == 'C' or md5_hash[0] == 'c'):
        partition_16 = 12
    elif (md5_hash[0] == 'D' or md5_hash[0] == 'd'):
        partition_16 = 13
    elif (md5_hash[0] == 'E' or md5_hash[0] == 'e'):
        partition_16 = 14
    elif (md5_hash[0] == 'F' or md5_hash[0] == 'f'):
        partition_16 = 15
    
    return partition_16 % pool_count if partition_16 != -1 else -1
    

if __name__ == "__main__":
    key = 'k5'
    print(md5_hash(key)[0], len(md5_hash(key)))
    print(request_route(3, key))