from __future__ import annotations

from typing import Dict, Type

from .base import BaseInvoiceTemplate
from .professional import ProfessionalInvoiceTemplate
from .rawayih import RawayihInvoiceTemplate
from .simple import SimpleInvoiceTemplate
from .standard import StandardInvoiceTemplate

TemplateRegistry = Dict[str, Dict[str, Type[BaseInvoiceTemplate]]]

AVAILABLE_TEMPLATES: TemplateRegistry = {
    "standard": {
        "name": "فاتورة ضريبية مبسطة",
        "description": "نموذج كامل مع QR Code وتفاصيل ضريبية كاملة",
        "class": StandardInvoiceTemplate,
    },
    "simple": {
        "name": "فاتورة بسيطة",
        "description": "نموذج سريع بدون QR مع تفاصيل بسيطة",
        "class": SimpleInvoiceTemplate,
    },
    "professional": {
        "name": "فاتورة ضريبية كاملة",
        "description": "نموذج احترافي بتصميم متطور ومعلومات إضافية",
        "class": ProfessionalInvoiceTemplate,
    },
    "rawayih": {
        "name": "فاتورة روائح بيتك",
        "description": "نموذج بتصميم بني/بيج مع QR وتفاصيل كاملة",
        "class": RawayihInvoiceTemplate,
    },
}

__all__ = [
    "BaseInvoiceTemplate",
    "StandardInvoiceTemplate",
    "SimpleInvoiceTemplate",
    "ProfessionalInvoiceTemplate",
    "RawayihInvoiceTemplate",
    "AVAILABLE_TEMPLATES",
]