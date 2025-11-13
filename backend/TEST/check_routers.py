"""Verifica qué routers están siendo cargados"""

from src.api.routes import routers

print(f"Total routers: {len(routers)}\n")
for i, (router, prefix, tags) in enumerate(routers, 1):
    print(f"{i}. {prefix:30s} - {tags}")
