## Prepare redis

```text
$ redis-cli -v                      
redis-cli 3.0.6
```

If you don't have redis, you need to install it.

## Setting

Edit the `settings.py`, change it to:

```python
import os

from toapi.cache import RedisCache, JsonSerializer
from toapi.settings import Settings

class MySettings(Settings):
    """
    Create custom configuration
    http://www.toapi.org/topics/settings/
    """

    cache = {
        'cache_class': RedisCache,
        'cache_config': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0
        },
        'serializer': JsonSerializer,
        'ttl': 10000
    }
    storage = {
        "PATH": os.getcwd(),
        "DB_URL": None
    }
    web = {
        "with_ajax": False,
        "request_config": {},
        "headers": None
    }
```

Try to run command `toapi run`. If it works, you do good job. 
If something wrong, please check the redis and the redis library for python.