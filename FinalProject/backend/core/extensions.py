"""Flask extensions — initialised without an app instance.

Extensions are created here in an uninitialised state and later bound to
the Flask application via ``init_app()`` inside the application factory
(``create_app`` in *app.py*).  This avoids circular imports because route
modules can import the extension objects at the module level without
needing a reference to the app.
"""

from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# CORS — configured with init_app() in the factory
cors = CORS()

# Rate limiter — no default limits; per-route limits applied via decorators.
# Counters are kept in memory: fine for one server process (Gunicorn runs a
# single worker with threads, see backend/Dockerfile). Several servers would
# need a shared store such as Redis.
limiter = Limiter(key_func=get_remote_address, default_limits=[], storage_uri='memory://')
