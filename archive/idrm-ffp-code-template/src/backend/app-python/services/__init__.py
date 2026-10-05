# Makes `services` an importable package. Business logic lives here (no HTTP/
# routing) — route handlers in `api/v1/` stay thin and just call these functions.
# M2 adds auth_service; later modules add service_service, geo_service, etc.
