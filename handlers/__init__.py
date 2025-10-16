from .start import router as start_router
from .patient_handlers import router as patient_router
from .admin_handlers import router as admin_router

__all__ = ['start_router', 'patient_router', 'admin_router']