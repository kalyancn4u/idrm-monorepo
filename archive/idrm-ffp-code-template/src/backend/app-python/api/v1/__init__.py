# Makes `api.v1` an importable package — one module per feature area, each
# exposing an APIRouter that main.py mounts under settings.API_V1_PREFIX.
# M2 adds: auth, users.  Later: services (M3), geo (M4), notifications (M5),
# analytics (M6).
