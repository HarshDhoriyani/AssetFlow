# models/maintenance_part.py

from odoo import models, fields


class MaintenancePart(models.Model):
    _name = 'assetflow.maintenance.part'
    _description = 'Maintenance Part'

    name = fields.Char(string='Name')
