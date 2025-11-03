from odoo import fields, models

class PosConfig(models.Model):
    _inherit="pos.config"
    
    tid = fields.Char('TID', help='Termial ID for the POS', size=8)
    mid = fields.Char('MID', help='Merchiant ID for the POS', size=15)