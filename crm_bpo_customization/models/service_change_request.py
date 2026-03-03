from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceChangeRequest(models.Model):
    """
    Manages post-go-live modifications for DID/SIP services (Increases/Decreases/Cancellations).
    Linked to the original CRM Lead for historical tracking.
    """
    _name = 'service.change.request'
    _description = 'Service Change Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # --- Basic Information ---
    name = fields.Char(string="Reference", readonly=True, copy=False, default=lambda self: _('New'))
    
    # Links the request to the original won Opportunity (DID/SIP Team only)
    lead_id = fields.Many2one(
        'crm.lead', 
        string="Active Service", 
        domain="[('team_id.name', 'ilike', 'DID'), ('probability', '=', 100)]",
        required=True, tracking=True
    )
    
    partner_id = fields.Many2one(related='lead_id.partner_id', string="Customer", store=True)

    # --- Change Specifics ---
    change_type = fields.Selection([
        ('channel_increase', 'Channel Increase'),
        ('channel_decrease', 'Channel Decrease'),
        ('did_add', 'DID Add'),
        ('did_remove', 'DID Remove'),
        ('service_cancellation', 'Service Cancellation')
    ], string="Change Type", required=True, tracking=True)

    # --- Workflow States ---
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Pending Approval'),
        ('approved', 'Approved by Tamer'),
        ('done', 'Billed & Completed'),
        ('cancel', 'Rejected')
    ], default='draft', string="Status", tracking=True)

    # --- Financial & Effective Dates ---
    effective_date = fields.Date(string="Effective Date", required=True, tracking=True)
    billing_impact = fields.Float(string="Monthly Billing Impact (+/-)", tracking=True)
    currency_id = fields.Many2one(related='lead_id.currency_id', string="Currency")

    description = fields.Text(string="Change Description", required=True)
    internal_notes = fields.Text(string="Internal Notes")

    # =================================================================
    # LOGIC & AUTOMATIONS
    # =================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """ Assigns unique SCR sequence numbers. Updated for Odoo 18 Batch Create. """
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('service.change.request') or _('New')
        return super(ServiceChangeRequest, self).create(vals_list)

    def action_confirm(self):
        """ Confirms request and notifies Tamer for commercial approval """
        self.ensure_one()
        self.state = 'confirmed'
        tamer_user = self.env['res.users'].search([('name', 'ilike', 'Tamer')], limit=1)
        if tamer_user:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=tamer_user.id,
                summary=_("Approval Required: %s") % self.change_type
            )

    def action_approve(self):
        """ Tamer's commercial approval action """

        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise ValidationError("Access Denied: Only Tamer (Sales Manager) can approve this request!")
        self.state = 'approved'
        self.message_post(body=_("Commercial approval granted by Tamer."))

    def action_done(self):
        """ Finalizes the change and forces an email notification to Islam """
        self.state = 'done'
        
        islam_user = self.env['res.users'].search([('name', 'ilike', 'Islam')], limit=1)
        
        if not islam_user or not islam_user.email:
            self.message_post(body=" Warning: Billing email could not be sent. User 'Islam' not found or has no email.")
            return

        body_html = f"""
            <div style="font-family: Arial, sans-serif; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                <h2 style="color: #1e4a6d; border-bottom: 2px solid #1e4a6d; padding-bottom: 10px;">
                    Billing Activation Request
                </h2>
                <p>Hello Islam,</p>
                <p>A new service change has been approved and is ready for billing:</p>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Reference:</b></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{self.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Customer:</b></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{self.partner_id.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Change Type:</b></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{self.change_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Billing Impact:</b></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{self.billing_impact} {self.currency_id.symbol or ''}</td>
                    </tr>
                </table>
                <p style="margin-top: 20px;">
                    <a href="/web#id={self.id}&model={self._name}&view_type=form" 
                       style="background-color: #1e4a6d; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">
                       View Request in Odoo
                    </a>
                </p>
                <p style="font-size: 12px; color: #888; margin-top: 30px;">
                    This is an automated notification from the CRM Service Management System.
                </p>
            </div>
        """

        mail_values = {
            'subject': f'URGENT: Billing Activation - {self.partner_id.name}',
            'body_html': body_html,
            'email_to': islam_user.email,
            'email_from': self.env.user.email or self.env.company.email,
        }
        
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()
        
        self.message_post(body=f" Billing notification email successfully sent to {islam_user.email}")

    def action_cancel(self):
        """ Rejects or cancels the request """
        self.state = 'cancel'