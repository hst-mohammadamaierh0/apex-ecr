from odoo import models, fields

class CsmenaEntity(models.Model):
    _name = 'csmena.entity'
    _description = 'CsMENA Contracting Entity'
    name = fields.Char(required=True)

class BpoService(models.Model):
    _name = 'bpo.service'
    _description = 'BPO Services'
    name = fields.Char(required=True)

class BpoChannel(models.Model):
    _name = 'bpo.channel'
    _description = 'BPO Channels'
    name = fields.Char(required=True)

class BpoContractType(models.Model):
    _name = 'bpo.contract.type'
    _description = 'BPO Contract Types'
    name = fields.Char(required=True)

class BpoObjection(models.Model):
    _name = 'bpo.objection'
    _description = 'BPO Client Objections'
    name = fields.Char(required=True)

class IshbekModule(models.Model):
    _name = 'ishbek.module'
    _description = 'ISHBEK Modules'
    name = fields.Char(required=True)

class IshbekPosSystem(models.Model):
    _name = 'ishbek.pos.system'
    _description = 'ISHBEK POS Systems'
    name = fields.Char(required=True)

class IshbekDeliveryIntegration(models.Model):
    _name = 'ishbek.delivery.integration'
    _description = 'ISHBEK Delivery Platforms'
    name = fields.Char(required=True)