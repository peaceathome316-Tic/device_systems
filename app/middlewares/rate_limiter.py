from slowapi import Limiter
from slowapi.util import get_remote_address

# Identifica a cada cliente por su IP para contar sus peticiones
limiter = Limiter(key_func=get_remote_address)