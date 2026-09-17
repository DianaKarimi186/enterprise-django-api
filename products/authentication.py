from rest_framework.authentication import SessionAuthentication


class HTMXSessionAuthentication(SessionAuthentication):
    """Authenticate browser-based HTMX requests using Django sessions."""

    pass
