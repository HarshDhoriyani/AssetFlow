# models/allocation.py

from odoo import models, fields


class Allocation(models.Model):
    _name = 'assetflow.allocation'
    _description = 'Allocation'

    name = fields.Char(string='Reference')
