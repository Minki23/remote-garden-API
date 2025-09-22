broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/0"

beat_scheduler = "redbeat.RedBeatScheduler"
timezone = "UTC"
enable_utc = True

beat_max_loop_interval = 10
redbeat_lock_timeout = 300
redbeat_redis_url = "redis://redis:6379/0"
worker_concurrency = 1
task_send_sent_event = True
worker_send_task_events = True
