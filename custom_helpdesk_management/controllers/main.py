# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CustomWebsiteHelpdesk(http.Controller):

    @http.route(['/submit-ticket'], type='http', auth="user", website=True)
    def my_custom_ticket_form(self, **kwargs):
       
        user = request.env.user
        employee = user.sudo().employee_id
        
        if not employee or not employee.department_id:
            return request.render("website.403")

        allowed_depts = employee.department_id.accessible_department_ids

        return request.render("custom_helpdesk_management.my_new_ticket_template", {
            'departments': allowed_depts, 
            'user': user
        })

    @http.route(['/ticket/submitted'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def handle_ticket_submission(self, **post):
       
        subject = post.get('subject')
        description = post.get('description')
        
        dept_id = int(post.get('department_id')) if post.get('department_id') else False
        cat_id = int(post.get('category_id')) if post.get('category_id') else False

        if not subject or not dept_id:
            return request.redirect('/submit-ticket?error=1')

        department = request.env['hr.department'].sudo().browse(dept_id)
        team_id = department.helpdesk_team_id.id if department.helpdesk_team_id else False

       
        ticket = request.env['helpdesk.ticket'].sudo().create({
            'name': subject,
            'description': description,
            'department_id': dept_id,
            'category_id': cat_id,
            'team_id': team_id,
            'partner_id': request.env.user.partner_id.id,
            'priority': '0', 
        })

        return request.render("custom_helpdesk_management.ticket_success_page", {
            'ticket': ticket
        })