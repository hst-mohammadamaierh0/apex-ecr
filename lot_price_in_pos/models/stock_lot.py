from odoo import models, fields

class StockLot(models.Model):
    _inherit = "stock.lot"

    lot_price = fields.Float(string="Lot Price", help="Custom price for this lot/serial")
