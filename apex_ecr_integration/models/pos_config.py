# -*- coding: utf-8 -*-
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    apex_ecr_enabled = fields.Boolean(
        string="Enable Apex ECR",
        default=False,
        help="Activate Apex ECR integration for this POS."
    )
    apex_tid = fields.Char(
        string="Terminal ID",
        help="Unique terminal ID assigned by the Apex ECR system."
    )
    apex_mid = fields.Char(
        string="Merchant ID",
        help="Merchant ID assigned by the Apex ECR system."
    )

    apex_secure_key = fields.Char(
        string="Merchant Secure Key",
        help="Secure key for authenticating with Apex ECR.")
    
    apex_ecr_test_mode = fields.Boolean(
        string="Apex ECR Test Mode",
        default=False,
        help="Enable this to simulate approved payments without connecting to the real Apex ECR terminal."
    )



class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    apex_ecr_enabled = fields.Boolean(
        string="Enable Apex ECR",
        help="Enable Apex ECR payment for this payment method."
    )
    apex_tid = fields.Char(
        string="Apex TID",
        help="Terminal ID linked to this payment method."
    )
    apex_mid = fields.Char(
        string="Apex MID",
        help="Merchant ID linked to this payment method."
    )
    apex_secure_key = fields.Char(
        string="Merchant Secure Key",
        help="Secure key for authenticating with Apex ECR.")
    
    

