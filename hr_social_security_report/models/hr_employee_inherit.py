from odoo import models, fields, api

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    social_security_ids = fields.One2many(
        'social.security.record',
        'employee_id',
        string='Social Security Records'
    )
    
    employee_code = fields.Char(
        string='Employee Code',
        default=lambda self: self._generate_employee_code(),
        readonly=True
    )
    
    @api.model
    def _generate_employee_code(self):
        """Generate sequential employee code: EMP001, EMP002, etc."""
        last_employee = self.search([], order='id desc', limit=1)
        if last_employee and last_employee.employee_code and last_employee.employee_code.startswith('EMP'):
            try:
                # Extract number from last code: EMP001 → 1
                last_num = int(last_employee.employee_code[3:])
                return f"EMP{last_num + 1:03d}"
            except:
                pass
        return "EMP001"
    
    def action_open_ss_wizard(self):
        """Open social security report wizard"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Social Security Report',
            'res_model': 'social.security.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
                'active_id': self.id,
                'active_model': 'hr.employee',
            }
        }