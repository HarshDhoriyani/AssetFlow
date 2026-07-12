# -*- coding: utf-8 -*-
{
    "name": "AssetFlow - Enterprise Asset & Resource Management",
    "version": "17.0.1.0.0",
    "summary": "AI-powered Enterprise Asset & Resource Management System",
    "description": """
AssetFlow - Intelligent Inventory & Asset Management
=====================================================
- Asset Registration & Lifecycle Management
- Asset Allocation & Transfer Workflows
- Maintenance Request Workflow
- Audit Cycle Workflow
- AI-Powered Predictive Maintenance
- Demand Forecasting (SMA & EWMA)
- Real-time Dashboards & Analytics
    """,
    "category": "Operations/Assets",
    "author": "AssetFlow Team",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
        "product",
        "stock",
        "account_asset",
        "maintenance",
        "board",
    ],
    "data": [
        "security/assetflow_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/demo_data.xml",
        "data/cron_jobs.xml",
        "data/automation_actions.xml",
        "views/dashboard.xml",
        "views/prediction_views.xml",
        "views/forecast_views.xml",
        "views/stock_views.xml",
        "views/asset_views.xml",
        "views/maintenance_views.xml",
        "views/audit_views.xml",
        "views/transfer_views.xml",
        "views/menu.xml",
        "reports/asset_report.xml",
        "reports/maintenance_report.xml",
        "reports/audit_report.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
