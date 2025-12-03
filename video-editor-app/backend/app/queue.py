from rq import Queue
from redis import Redis
from .config import settings


redis_conn = Redis.from_url(settings.REDIS_URL)
queue = Queue("renders", connection=redis_conn)
