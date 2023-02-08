{
    "name": "Automatic Perception",
    "summary": """
       This module creates a automatic perceptions.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["PerezGabriela"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Accounting",
    "version": "11.0.1.1.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": ['account_padron_retention_perception'],
    "data": [
        "views/account_padron_retention_perception_type_views.xml",
    ],
}
