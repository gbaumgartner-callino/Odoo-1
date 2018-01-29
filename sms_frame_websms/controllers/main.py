# -*- coding: utf-8 -*-
import openerp.http as http
from openerp.http import request

class WebsmsController(http.Controller):

    @http.route('/sms/websms/receipt', type="http", auth="public", csrf=False)
    def sms_websms_receipt(self, **kwargs):
        """Update the state of a sms message, don't trust the posted data"""
        
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        request.env['sms.gateway.websms'].sudo().delivary_receipt(values['AccountSid'], values['MessageSid'])
        
        return "<Response></Response>"
        
    @http.route('/sms/websms/receive', type="http", auth="public", csrf=False)
    def sms_websms_receive(self, **kwargs):
        """Fetch the new message directly from Websms, don't trust posted data"""
        
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        
        websms_account = request.env['sms.account'].sudo().search([('websms_account_sid','=', values['AccountSid'])])
        request.env['sms.gateway.websms'].sudo().check_messages(websms_account.id, values['MessageSid'])
        
        return "<Response></Response>"