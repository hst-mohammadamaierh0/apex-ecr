from odoo import models, api
from datetime import datetime

class SocialSecurityReport(models.AbstractModel):
    _name = 'report.hr_social_security_report.social_security_template'
    _description = 'Social Security Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Generate report values"""
        if not docids:
            docids = [data.get('employee_id')] if data and data.get('employee_id') else []
        
        docs = self.env['hr.employee'].browse(docids)
        
        # Initialize totals
        totals = {
            'total_employee': 0.0,
            'total_company': 0.0,
            'grand_total': 0.0,
        }
        
        filtered_records = False
        if docs and data and data.get('year'):
            # Filter records by year
            year = str(data.get('year'))
            filtered_records = docs.social_security_ids.filtered(
                lambda r: str(r.year) == year
            )
            
            # Calculate totals for filtered records
            if filtered_records:
                totals['total_employee'] = sum(filtered_records.mapped('employee_contribution'))
                totals['total_company'] = sum(filtered_records.mapped('company_contribution'))
                totals['grand_total'] = sum(filtered_records.mapped('total'))
        
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': docs,
            'data': data,
            'filtered_records': filtered_records,
            'totals': totals,
            'format_decimal': lambda x: '{:,.2f}'.format(x) if x else '0.00',
            'current_datetime': datetime.now(),  # Pass the actual datetime object
        }