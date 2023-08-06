#!../venv/bin/python
import threading, time
from app import cache, stats, dummy_stat, total_stat, DEFAULT_CAPACITY, DEFAULT_POLICY
import db_operations
import aws_operations
import random

def update_stat_thread():
    while True:
        if (len(stats) < 1):
            stats.append(dummy_stat.copy())
        else:
            removed_stat = stats.popleft()
            stats.append(dummy_stat.copy())
            # total_stat['no_items'] -= removed_stat['no_items']
            # total_stat['total_size'] -= removed_stat['total_size']
            total_stat['no_request'] -= removed_stat['no_request']
            total_stat['miss_rate'] -= removed_stat['miss_rate']
            total_stat['hit_rate'] -= removed_stat['hit_rate']

        # total_stat['no_items'] += dummy_stat['no_items']
        # total_stat['total_size'] += dummy_stat['total_size']
        total_stat['no_request'] += dummy_stat['no_request']
        total_stat['miss_rate'] += dummy_stat['miss_rate']
        total_stat['hit_rate'] += dummy_stat['hit_rate']

        # dummy_stat['no_items'] = 0
        # dummy_stat['total_size'] = 0
        dummy_stat['no_request'] = 0
        dummy_stat['miss_rate'] = 0
        dummy_stat['hit_rate'] = 0
        
        # db_operations.put_memcache_stats(total_stat)
        print(total_stat)
        aws_operations.post_custom_metric('us-east-1', 0, total_stat)





        time.sleep(5)

if __name__ == '__main__':
    # db_operations.initialize_memcache_stats(total_stat)
    # db_operations.put_memcache_config(capacity=DEFAULT_CAPACITY, policy=DEFAULT_POLICY)
    threading.Thread(target=update_stat_thread, daemon=True).start()
    cache.run('0.0.0.0', 5001, debug=False)

