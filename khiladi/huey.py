from huey import RedisHuey
import json

huey = RedisHuey('sharekhiladi', host='localhost', port=6379, result_store=True, serializer=json)
