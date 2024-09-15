import os
import logging
from elasticsearch import AsyncElasticsearch
from functools import lru_cache
import asyncio

logger = logging.getLogger(__name__)


class ServiceLocator:
    def __init__(self):
        self.es_host = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
        self.es_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.es_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.es_client = None

    async def get_elasticsearch_client(self):
        if self.es_client is None:
            try:
                self.es_client = AsyncElasticsearch(
                    [
                        {
                            "host": self.es_host,
                            "port": self.es_port,
                            "scheme": self.es_scheme,
                        }
                    ]
                )
                await self.es_client.ping()
            except Exception as e:
                logger.error(f"Failed to connect to Elasticsearch: {e}")
                self.es_client = None
        return self.es_client


service_locator = ServiceLocator()
