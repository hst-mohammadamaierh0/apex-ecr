# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # The target department for the ticket
    department_id = fields.Many2one(
        'hr.department', 
        string='Target Department', 
        required=True,
        tracking=True
    )

    team_member_ids = fields.Many2many(related='team_id.member_ids', string="Team Members")
    category_id = fields.Many2one('hr.department.category', string='Category')


    user_id = fields.Many2one(
        'res.users', 
        string='Assigned to',
        tracking=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Automated Assignment: Assigns the ticket to the eligible team member 
        with the least number of open tickets.
        """
        for vals in vals_list:
            if vals.get('department_id') and vals.get('team_id'):
                team = self.env['helpdesk.team'].browse(vals['team_id'])
                
                # Filter members: Must belong to the team, match the target department, and not be on leave
                eligible_members = team.member_ids.filtered(
                    lambda m: m.employee_id.department_id.id == vals['department_id'] 
                    and not m.employee_id.is_absent
                )

                if eligible_members:
                    member_load = []
                    for member in eligible_members:
                        # Count active (not closed) tickets assigned to the member
                        count = self.search_count([
                            ('user_id', '=', member.id),
                            ('stage_id.fold', '=', False)
                        ])
                        member_load.append((count, member.id))
                    
                    # Sort by ticket count and pick the first one (least busy)
                    member_load.sort()
                    vals['user_id'] = member_load[0][1]
        
        return super(HelpdeskTicket, self).create(vals_list)

    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Automatically sets the team responsible for the selected department."""
        if self.department_id and self.department_id.helpdesk_team_id:
            self.team_id = self.department_id.helpdesk_team_id
        else:
            self.team_id = False

    @api.constrains('department_id')
    def _check_department_sending_rights(self):
        """
        Security Constraint: Ensures the user only sends tickets to 
        departments allowed by their own department settings.
        """
        for record in self:
            # Skip validation for Administrators or Helpdesk Managers
            if self.env.is_admin() or self.env.user.has_group('helpdesk.group_helpdesk_manager'):
                continue
            
            user_employee = self.env.user.employee_id
            if not user_employee:
                raise ValidationError(_("Error: You must have an Employee profile linked to your user to submit tickets."))

            # Retrieve the list of departments allowed for the current user's department
            allowed_depts = user_employee.department_id.accessible_department_ids
            
            if record.department_id not in allowed_depts:
                raise ValidationError(_(
                    "Security Error: You do not have permission to send tickets to the '%s' department. "
                    "Your access is restricted to departments authorized for your team."
                ) % record.department_id.name)
        
    @api.model
    def website_form_send(self, values):
        if 'category_id' in values:
            values['category_id'] = int(values['category_id'])
        return super(HelpdeskTicket, self).website_form_send(values)

class HrDepartmentCategory(models.Model):
    _name = 'hr.department.category'
    _description = 'Department Category Details'

    name = fields.Char(string='Category Name', required=True)

    department_id = fields.Many2one('hr.department', string='Department', ondelete='cascade')


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    helpdesk_team_id = fields.Many2one(
        'helpdesk.team', 
        string='Responsible Helpdesk Team',
        help="The specific Helpdesk team that handles tickets for this department."
    )

    accessible_department_ids = fields.Many2many(
        'hr.department', 
        'dept_access_rel', 
        'source_dept_id', 
        'target_dept_id', 
        string='Can Send Tickets To',
        help="Define which departments the employees of this department are allowed to contact."
    )

    dept_category_ids = fields.One2many(
        'hr.department.category', 
        'department_id', 
        string='Department Categories'
    )

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    department_id = fields.Many2one(
        'hr.department', 
        string='Department', 
        help="The department linked to this helpdesk team."
    )