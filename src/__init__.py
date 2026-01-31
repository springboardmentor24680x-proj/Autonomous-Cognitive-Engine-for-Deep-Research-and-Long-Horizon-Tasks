from .logging_config import configure_logging

# Ensure logging is configured on package import so modules can call `get_logger()` safely.
configure_logging()
