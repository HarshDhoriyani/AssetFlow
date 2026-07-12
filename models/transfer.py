# models/transfer.py

from odoo import models, fields


class Transfer(models.Model):
    _name = 'assetflow.transfer'
    _description = 'Transfer'

    name = fields.Char(string='Reference')
