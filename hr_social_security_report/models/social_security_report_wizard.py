from odoo import models, fields, api
from datetime import datetime

class SocialSecurityReportWizard(models.TransientModel):
    _name = 'social.security.report.wizard'
    _description = 'Social Security Report Wizard'

    year = fields.Selection(
        selection='_get_year_selection',
        string='Year',
        required=True
    )
    
    employee_id = fields.Many2one(
        'hr.employee', 
        string='Employee',
        required=True,
        default=lambda self: self._default_employee()
    )

    @api.model
    def _get_year_selection(self):
        """Get available years from social security records"""
        current_year = datetime.now().year
        years = []
        
        try:
            records = self.env['social.security.record'].search([])
            if records:
                years = list(set(records.mapped('year')))
                years = sorted(years, reverse=True)
            else:
                years = [str(year) for year in range(current_year, current_year - 5, -1)]
        except:
            years = [str(current_year), str(current_year - 1)]
        
        return [(year, year) for year in years]

    @api.model
    def _default_employee(self):
        """Get default employee from context"""
        context = self.env.context
        if context.get('active_model') == 'hr.employee' and context.get('active_id'):
            return context.get('active_id')
        return False

    @api.model
    def default_get(self, fields_list):
        """Set default values"""
        res = super().default_get(fields_list)
        
        if self.env.context.get('active_model') == 'hr.employee':
            employee_id = self.env.context.get('active_id')
            if employee_id:
                res['employee_id'] = employee_id
                
                employee = self.env['hr.employee'].browse(employee_id)
                if employee and employee.social_security_ids:
                    years = list(set(employee.social_security_ids.mapped('year')))
                    if years:
                        res['year'] = sorted(years, reverse=True)[0]
        
        return res
    
    def print_report(self):
        """Generate report"""
        self.ensure_one()
        
        report_action = self.env.ref('hr_social_security_report.action_social_security_report')
        
        return report_action.report_action(
            docids=[self.employee_id.id],
            data={
                'year': str(self.year),
                'employee_id': self.employee_id.id,
            }
        )