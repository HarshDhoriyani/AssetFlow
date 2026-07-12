# models/maintenance_request.py

from odoo import models, fields


class MaintenanceRequest(models.Model):
    _name = 'assetflow.maintenance.request'
    _description = 'Maintenance Request'

    name = fields.Char(string='Reference')
