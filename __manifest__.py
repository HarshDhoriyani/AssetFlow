# -*- coding: utf-8 -*-
{
    'name': 'AssetFlow - Enterprise Asset & Resource Management',
    'version': '17.0.1.0.0',
    'summary': 'AI-powered Enterprise Asset & Resource Management System',
    'description': """
AssetFlow - Core ERP Backend (Member 1 scope)
==============================================
Provides the operational backbone for the AssetFlow system:

- Asset Registration & Lifecycle Management
- Asset Categories & Tags
- Asset Allocation Workflow
- Asset Transfer Workflow
- Maintenance Request Workflow
- Audit Cycle Workflow
- Role-based Security & Record Rules

This module is designed to be the foundation that the AI & Automation layer
(Member 2) and the Frontend/Dashboard layer (Member 3) build on top of.
    """,
    'category': 'Operations/Assets',
    'author': 'AssetFlow Team - Member 1 (Core ERP Backend)',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'hr',
        'product',
    ],
    'data': [
        # security
        'security/assetflow_security.xml',
        'security/ir.model.access.csv',
        # data
        'data/ir_sequence_data.xml',
        # views
        'views/asset_category_views.xml',
        'views/asset_views.xml',
        'views/allocation_views.xml',
        'views/transfer_views.xml',
        'views/maintenance_views.xml',
        'views/audit_views.xml',
        'views/menu.xml',
        # reports
        'reports/asset_report.xml',
        'reports/maintenance_report.xml',
        'reports/audit_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
