from odoo import models, fields, api

class SocialSecurityRecord(models.Model):
    _name = 'social.security.record'
    _description = 'Employee Social Security Record'
    _order = 'year desc, id desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    year = fields.Char('Year', required=True)
    employee_code = fields.Char('Employee Code', related='employee_id.employee_code', store=True)
    
    # Keep as Selection field to avoid the cleanup error
    social_security_type = fields.Selection(
        [
            ('pension', 'Pension'),
            ('health', 'Health Insurance'),
            ('unemployment', 'Unemployment'),
            ('disability', 'Disability'),
            ('other', 'Other'),
        ],
        string='Social Security Type',
        default='pension'
    )
    
    social_code = fields.Char('Social Code')
    ss_base_salary = fields.Float('SS Base Salary')
    employee_contribution = fields.Float('Employee Contribution')
    company_contribution = fields.Float('Company Contribution')
    total = fields.Float('Total', compute='_compute_total', store=True)
    
    @api.depends('employee_contribution', 'company_contribution')
    def _compute_total(self):
        for record in self:
            record.total = record.employee_contribution + record.company_contribution