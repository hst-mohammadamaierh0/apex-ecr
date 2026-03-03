from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # --- HELPERS FOR VIEW LOGIC ---
    team_id_name = fields.Char(related='team_id.name', string="Sales Team Name", store=True)
    stage_id_name = fields.Char(related='stage_id.name', string="Stage Name", store=True)

    # --- STAGE 1 & 2: PROSPECT & DISCOVERY ---
    contact_role = fields.Selection([
        ('decision_maker', 'Decision Maker'),
        ('influencer', 'Influencer'),
        ('unknown', 'Unknown')
    ], string="Contact Role")
    
    interested_service_ids = fields.Many2many('bpo.service', string="Interested Service")
    bpo_country_id = fields.Many2one('res.country', string="Country")
    
    bpo_lead_source = fields.Selection([
        ('sales_team', 'Sales Team'),
        ('referral', 'Referral'),
        ('bid', 'BID')
    ], string="Lead Source")

    headcount_range = fields.Selection([
        ('0-10', '0–10'), ('10-30', '10–30'), ('30-50', '30–50'),
        ('100-150', '100–150'), ('150+', '150+')
    ], string="Headcount Range")

    client_type = fields.Selection([
        ('new', 'New Client'),
        ('hc_increase', 'Existing Client – HC Increase'),
        ('hc_decrease', 'Existing Client – HC Decrease'),
        ('bid', 'BID')
    ], string="Client Type")
    
    previous_project_id = fields.Many2one('project.project', string="Previous Project")
    channel_ids = fields.Many2many('bpo.channel', string="Channels Type")
    operating_hours = fields.Char("Expected Operating Hours")
    languages = fields.Char("Languages")
    tech_owner = fields.Selection([('client', 'Client'), ('csmena', 'CsMENA')], string="Technology Owner")
    expected_start_date = fields.Date("Expected Start Date")

    # --- STAGE 3 & 4: PRICING & PROPOSAL ---
    proposal_type = fields.Selection([('technical', 'Technical'), ('financial', 'Financial'), ('both', 'Both')], string="Proposal Type")
    proposal_validity = fields.Selection([('30', '30 Days'), ('90', '90 Days'), ('120', '120 Days')], string="Proposal Validity")
    currency_id = fields.Many2one('res.currency', string="Currency")
    submission_deadline = fields.Date("Submission Deadline")
    
    pricing_approved = fields.Boolean("Pricing Approved", default=False, tracking=True)
    approved_by_id = fields.Many2one('res.users', string="Approved By (Tamer)")
    
    # Mandatory Attachments
    technical_proposal_id = fields.Many2one('ir.attachment', string="Technical Proposal")
    financial_proposal_id = fields.Many2one('ir.attachment', string="Financial Proposal")

    # --- STAGE 5 & 6: NEGOTIATION & VERBAL ---
    objection_ids = fields.Many2many('bpo.objection', string="Client Objections")
    mod_requested = fields.Boolean("Modification Requested")
    mod_approval_status = fields.Selection([
        ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')
    ], string="Approval Status")
    
    verbal_conf_date = fields.Date("Verbal Confirmation Date")
    tentative_start_date = fields.Date("Tentative Start Date")
    tentative_headcount = fields.Integer("Tentative Headcount")

    # --- STAGE 7: CONTRACTING ---
    contract_type_ids = fields.Many2many('bpo.contract.type', string="Contract Type")
    client_legal_entity = fields.Char("Client Legal Entity")
    csmena_entity = fields.Selection([
        ('jordan', 'Al Raghad (Jordan)'),
        ('ksa', 'Al Raghad (KSA)'),
        ('egypt', 'Al Raghad (Egypt)')
    ], string="CsMENA Contracting Entity")
    
    payment_terms = fields.Selection([('30', '30 Days'), ('90', '90 Days'), ('120', '120 Days')], string="Payment Terms")
    billing_start_date = fields.Date("Billing Start Date")
    signature_status = fields.Boolean("Fully Signed")
    signed_contract_id = fields.Many2one('ir.attachment', string="Signed Contract")

    # --- STAGE 9: LOST ---
    bpo_loss_reason_ids = fields.Many2many('crm.lost.reason', string="BPO Loss Reasons")
    competitor_name = fields.Char("Competitor Name")
    competitor_pricing = fields.Selection([('lower', 'Lower'), ('similar', 'Similar'), ('higher', 'Higher')], string="Competitor Pricing Level")
    bid_cycle_duration = fields.Char("BID Cycle Duration")
    bid_cycle_reminder = fields.Date("Next BID Engagement Date")


    #--------------------------------------------------------
    # --- ISHBEK STAGE 1 & 2 ---
    restaurant_name = fields.Char("Restaurant Name")
    branch_count = fields.Integer("Number of Branches")
    ishbek_lead_source = fields.Selection([
        ('sales', 'Sales'), ('referral', 'Referral'), 
        ('partner', 'Partner'), ('inbound', 'Inbound')
    ], string="ISHBEK Lead Source")

    go_live_date = fields.Date("Go-Live Date")
    active_branches = fields.Integer("Number of Active Branches")
    
    # Stage 2: Demo
    demo_conducted = fields.Boolean("Demo Conducted")
    demo_date = fields.Date("Demo Date")
    use_case_fit = fields.Selection([
        ('full', 'Full'), ('partial', 'Partial'), ('not_suitable', 'Not Suitable')
    ], string="Use Case Fit")
    ishbek_module_ids = fields.Many2many('ishbek.module', string="Required Modules")
    discovery_notes = fields.Text("Discovery Notes")

    # Stage 5: Integrations
    pos_system_id = fields.Many2one('ishbek.pos.system', string="POS Integration")
    delivery_integration_ids = fields.Many2many('ishbek.delivery.integration', string="Other Integrations")
    integration_status = fields.Selection([
        ('pending', 'Pending'), ('done', 'Done'), ('challenge', 'Challenge')
    ], string="Integration Status")
    challenge_description = fields.Text("Challenge Description")

    # Stage 6: Menu Setup
    menu_data_received = fields.Boolean("Menu Data Received")
    menu_uploaded = fields.Boolean("Menu Uploaded")
    menu_approved = fields.Boolean("Menu Approved by Client")

    # Stage 8: Finance (Critical)
    price_per_branch = fields.Float("Price per Branch")
    ishbek_payment_term = fields.Selection([
        ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('annually', 'Annually')
    ], string="ISHBEK Payment Term")
    license_activation_date = fields.Date("License Activation Date")
    license_end_date = fields.Date("License End Date")
    billing_contact_name = fields.Char("Billing Contact Name")
    billing_contact_email = fields.Char("Billing Contact Email")



    #--------------------------------

    # --- STAGE 1 & 2: DID/SIP Specific Fields ---
    service_delivery_model = fields.Selection([
        ('direct', 'Direct (CsMENA DID / SIP)'),
        ('third_party', 'Third-Party Provider'),
        ('hybrid', 'Hybrid')
    ], string="Service Delivery Model")
    
    third_party_provider_name = fields.Char("Third-Party Provider Name")
    dids_country = fields.Many2one('res.country', string="DIDs Country")
    is_third_party_known = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Third-Party Provider Known?")

    # --- STAGE 2: Regulatory & Feasibility ---
    compliance_responsibility = fields.Selection([
        ('csmena', 'CsMENA'),
        ('third_party', 'Third-Party Provider')
    ], string="Compliance Responsibility")
    
    kyc_owner = fields.Selection([
        ('client', 'Client'),
        ('csmena', 'CsMENA'),
        ('third_party', 'Third-Party')
    ], string="KYC / Docs Owner")
    
    provider_feasibility = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Provider Feasibility Confirmed")
    provisioning_lead_time = fields.Integer("Provisioning Lead Time (Days)")

    # --- STAGE 3 & 4: Commercial & Pricing ---
    billing_model = fields.Selection([('prepaid', 'Prepaid'), ('postpaid', 'Postpaid')], string="Billing Model")
    sla_owner = fields.Selection([('csmena', 'CsMENA'), ('third_party', 'Third-Party (Back-to-back)')], string="SLA Owner")
    has_penalty = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Penalty Included")


    # --- DID/SIP STAGE 6 & 7: TESTING & CONTRACTING ---
    testing_start_date = fields.Date("Testing Start Date")
    testing_end_date = fields.Date("Testing End Date")
    testing_conducted_by = fields.Selection([
        ('csmena', 'CsMENA'),
        ('third_party', 'Third-Party'),
        ('joint', 'Joint')
    ], string="Testing Conducted By")
    
    client_acceptance_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Client Acceptance Required")
    testing_completed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Testing Completed")
    
    # (Stage 8)
    billing_start_date = fields.Date("Billing Start Date")
    
    # --- STAGE 8: Live / Billing Details ---
    did_price = fields.Float("DID Price")
    channel_count = fields.Integer("Number of Channels")
    channel_price = fields.Float("Channel Price")
    local_outbound_fee = fields.Float("Local Outbound Minute Fee")
    non_local_outbound_fee = fields.Float("Non-local Outbound Minute Fee")
    billing_mode = fields.Selection([
        ('30/30', '30/30'),
        ('60/30', '60/30'),
        ('60/60', '60/60')
    ], string="Billing Mode")
    one_time_fee = fields.Float("One-time Implementation Fee")
    taxes_amount = fields.Float("Taxes")

    did_pricing_approved = fields.Boolean("DID Pricing Approved", default=False, tracking=True)
    did_approved_by_id = fields.Many2one('res.users', string="Approved By (Tamer)", readonly=True)


    
    # --- VALIDATIONS ---
    @api.constrains('stage_id', 'pricing_approved', 'signature_status')
    def _check_bpo_stage_conditions(self):
        for lead in self:
          
            if lead.team_id and "BPO" in lead.team_id.name.upper():
                
               
                if lead.stage_id.name == 'PROPOSAL SENT' and not lead.pricing_approved:
                    raise ValidationError(_(
                        "STOP! Opportunity cannot move to 'PROPOSAL SENT' until Pricing is approved by Tamer. "
                        "Please check the 'Pricing Approved' box first."
                    ))
                
                if lead.stage_id.is_won and not lead.signature_status:
                    raise ValidationError(_(
                        "A 'Fully Signed' contract is mandatory before marking this Opportunity as WON!"
                    ))

    @api.constrains('service_delivery_model', 'third_party_provider_name', 'team_id')
    def _check_third_party_details(self):
        for lead in self:
            if lead.team_id.name == 'CS Technologies - DID/SIP Sales':
                if lead.service_delivery_model != 'direct' and not lead.third_party_provider_name:
                    raise ValidationError(_("For DID Sales: Third-Party Provider Name is mandatory when the model is not Direct!"))
                
    # --- AUTOMATIONS (STAGE 8: WON) ---
    def action_set_won_rainbowman(self):
        """
        """
        res = super(CrmLead, self).action_set_won_rainbowman()
        for lead in self:
            if lead.team_id and "BPO" in lead.team_id.name.upper():
                
                if lead.client_type in ['hc_increase', 'hc_decrease'] and lead.previous_project_id:
                    lead.previous_project_id.message_post(body=_(
                        "AUTOMATION: Project updated due to HC Change Request. New Range: %s, Effective Date: %s"
                    ) % (lead.headcount_range, fields.Date.today()))
                    lead.message_post(body=_("Log: Existing Project '%s' has been updated.") % lead.previous_project_id.name)
                
                else:
                    project = self.env['project.project'].create({
                        'name': f"BPO Project: {lead.partner_id.name or lead.contact_name} - {lead.name}",
                        'partner_id': lead.partner_id.id,
                        'description': f"""
                            <p><b>Commercial Handover Summary:</b></p>
                            <ul>
                                <li><b>Service Type:</b> {', '.join(lead.interested_service_ids.mapped('name'))}</li>
                                <li><b>Contractual Headcount:</b> {lead.headcount_range}</li>
                                <li><b>Operating Hours:</b> {lead.operating_hours or 'N/A'}</li>
                                <li><b>Languages:</b> {lead.languages or 'N/A'}</li>
                                <li><b>Confirmed Start Date:</b> {lead.expected_start_date or 'N/A'}</li>
                                <li><b>Client Contact:</b> {lead.partner_id.name}</li>
                            </ul>
                        """
                    })
                    lead.message_post(body=_("SUCCESS: Project '%s' has been created for Operations.") % project.name)
                
                lead.message_post(body=_("Finance department has been notified for billing and contract setup."))
        return res

    @api.onchange('bid_cycle_duration')
    def _set_bid_reminder(self):
        """
        """
        if self.bid_cycle_duration and self.bpo_lead_source == 'bid':
            self.bid_cycle_reminder = fields.Date.today() + timedelta(days=335)

    @api.onchange('pricing_approved')
    def _onchange_pricing_approved(self):
        if self.pricing_approved:
            if not self.env.user.has_group('sales_team.group_sale_manager'):
                raise ValidationError(_("Access Denied: Only Sales Managers (Tamer) can approve pricing!"))
            self.approved_by_id = self.env.user

    
    # --- AUTOMATION: SEND INVOICE TO USER
    def action_ishbek_send_invoice(self):
        """
      
        """
        for lead in self:
            
            islam_user = self.env['res.users'].search([('name', 'ilike', 'Islam')], limit=1)
            
            body = f"""
                <b>Invoice Request: {lead.restaurant_name}</b><br/>
                Branches: {lead.branch_count}<br/>
                Price per Branch: {lead.price_per_branch}<br/>
                Activation Date: {lead.license_activation_date}<br/>
                Billing Contact: {lead.billing_contact_name} ({lead.billing_contact_email})
            """
            
            lead.message_post(body=body, partner_ids=islam_user.partner_id.ids if islam_user else [])
            lead.message_post(body=_("Finance has been notified. Invoice request sent to Islam."))



    @api.constrains('stage_id')
    def _check_did_approval_before_proposal(self):
        for lead in self:
            if lead.team_id and "DID" in lead.team_id.name.upper():
                
                if lead.stage_id.sequence >= 205 and not lead.did_pricing_approved:
                    raise ValidationError(_(
                        "Access Denied: You cannot send the proposal until Tamer approves the pricing in Stage 4!"
                    ))
    
    def action_did_send_tamer_approval(self):
        for lead in self:
            tamer_user = self.env['res.users'].search([('name', 'ilike', 'Tamer')], limit=1)
            lead.message_post(
                body=f"<b>Pricing Approval Request</b>: Please approve the DID pricing sheet for {lead.partner_id.name}.",
                partner_ids=tamer_user.partner_id.ids if tamer_user else []
            )
            
            lead.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=tamer_user.id if tamer_user else self.env.user.id,
                summary=_("Pricing Approval Required for DID Sale")
            )


    def action_did_approve_pricing(self):
        for lead in self:
            if not self.env.user.has_group('sales_team.group_sale_manager'):
                raise ValidationError(_("Access Denied: Only Tamer (Sales Manager) can approve this pricing!"))
            
            lead.write({
                'did_pricing_approved': True,
                'did_approved_by_id': self.env.user.id
            })
            
            lead.message_post(body=_(" Pricing has been officially approved by Tamer."))


    def action_did_send_invoice(self):
        """ Finalizes the DID/SIP sale and notifies Islam via Email/Chatter """
        for lead in self:
            islam_user = self.env['res.users'].search([('name', 'ilike', 'Islam')], limit=1)
            
            body = f"""
                <div style="font-family: Arial, sans-serif; border: 1px solid #1e4a6d; padding: 15px; border-radius: 8px;">
                    <h3 style="color: #1e4a6d; margin-top: 0;"> DID/SIP Billing Activation Request</h3>
                    <p><b>Client:</b> {lead.partner_id.name}</p>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background-color: #f8f9fa;">
                            <td style="padding: 5px; border: 1px solid #ddd;"><b>Channels:</b></td>
                            <td style="padding: 5px; border: 1px solid #ddd;">{lead.channel_count} (Price: {lead.channel_price})</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px; border: 1px solid #ddd;"><b>DID Price:</b></td>
                            <td style="padding: 5px; border: 1px solid #ddd;">{lead.did_price}</td>
                        </tr>
                        <tr style="background-color: #f8f9fa;">
                            <td style="padding: 5px; border: 1px solid #ddd;"><b>Billing Mode:</b></td>
                            <td style="padding: 5px; border: 1px solid #ddd;">{lead.billing_mode}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px; border: 1px solid #ddd;"><b>Local Min Fee:</b></td>
                            <td style="padding: 5px; border: 1px solid #ddd;">{lead.local_outbound_fee}</td>
                        </tr>
                        <tr style="background-color: #f8f9fa;">
                            <td style="padding: 5px; border: 1px solid #ddd;"><b>Implementation Fee:</b></td>
                            <td style="padding: 5px; border: 1px solid #ddd;">{lead.one_time_fee}</td>
                        </tr>
                    </table>
                    <p style="margin-top: 15px;"><i>Please process the billing for this client immediately.</i></p>
                </div>
            """
            
            lead.message_post(body=body, partner_ids=islam_user.partner_id.ids if islam_user else [])
            
            if islam_user and islam_user.email:
                mail_values = {
                    'subject': f'Billing Activation: {lead.partner_id.name}',
                    'body_html': body,
                    'email_to': islam_user.email,
                }
                self.env['mail.mail'].sudo().create(mail_values).send()
            
            lead.message_post(body=" Billing notification has been sent to Islam.")

    def action_set_won(self):
        """ Fix for AttributeError: Correcting field names for automation """
        res = super(CrmLead, self).action_set_won()
        for lead in self:
            if lead.team_id and 'BPO' in lead.team_id.name.upper():
                service_info = lead.interested_service if hasattr(lead, 'interested_service') else 'N/A'
                
                self.env['project.project'].sudo().create({
                    'name': f"Project: {lead.name}",
                    'partner_id': lead.partner_id.id,
                    'description': f"""
                        Service: {service_info}
                        Headcount: {lead.headcount_range if hasattr(lead, 'headcount_range') else 'N/A'}
                        Operating Hours: {lead.operating_hours if hasattr(lead, 'operating_hours') else 'N/A'}
                    """,
                })
        return res

