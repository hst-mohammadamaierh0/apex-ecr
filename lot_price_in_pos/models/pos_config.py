from odoo import models, fields

class PosConfig(models.Model):
    _inherit = "pos.config"

    use_lot_price = fields.Boolean(
        string="Enable Lot Price in POS",
        default=True,
        help="Automatically use the Lot/Serial Price when selecting a lot in the POS."
    )
