from core.config import CONFIG

broker_url = f"redis://{CONFIG.REDIS_HOST}:{CONFIG.REDIS_PORT}/0"
result_backend = f"redis://{CONFIG.REDIS_HOST}:{CONFIG.REDIS_PORT}/0"

beat_scheduler = "redbeat.RedBeatScheduler"
timezone = "UTC"
enable_utc = True

beat_max_loop_interval = 10
redbeat_lock_timeout = 300
redbeat_redis_url = f"redis://{CONFIG.REDIS_HOST}:{CONFIG.REDIS_PORT}/0"

worker_concurrency = 1
task_send_sent_event = True
worker_send_task_events = True
