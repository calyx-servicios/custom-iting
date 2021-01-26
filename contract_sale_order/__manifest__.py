# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Contract Sale Order",
    "summary": """
        Create a sale order from contract""",
    "author": "Calyx Servicios S.A.",
    "maintainers": ["JhoneM"],
    "website": "http://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Contract",
    "version": "11.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["contract", "sale", "analytic"],
    "data": [
        "views/contract_view.xml",
        "views/sale_order_view.xml",
        "data/contract_cron.xml",
    ],
}
