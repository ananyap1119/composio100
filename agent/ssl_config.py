"""Shared safe TLS configuration for outbound HTTPS clients."""

import os

_configured = False


def configure_ssl() -> None:
    """Use the OS trust store, falling back to certifi without disabling verification."""
    global _configured
    if _configured:
        return
    try:
        import truststore

        truststore.inject_into_ssl()
    except (ImportError, NotImplementedError, RuntimeError):
        import certifi

        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    _configured = True
