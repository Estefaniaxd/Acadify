
import redis.asyncio as redis_async
from src.core.config import settings

class RedisService:
	def __init__(self):
		self.redis_url = settings.REDIS_URL
		self.client = None

	async def connect(self):
		self.client = await redis_async.from_url(self.redis_url, decode_responses=True)

	async def disconnect(self):
		if self.client:
			await self.client.close()
			self.client = None
