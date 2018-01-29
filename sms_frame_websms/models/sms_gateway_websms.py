# -*- coding: utf-8 -*-
import requests
from datetime import datetime
from lxml import etree
import logging

_logger = logging.getLogger(__name__)
import base64
import urlparse

from openerp.http import request
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError


class sms_response():
    delivary_state = ""
    response_string = ""
    human_read_error = ""
    mms_url = ""
    message_id = ""


class SmsGatewayWebsms(models.Model):
    _name = "sms.gateway.websms"
    _description = "Websms SMS Gateway"

    api_url = fields.Char(string='API URL')

    def send_message(self, sms_gateway_id, from_number, to_number, sms_content, my_model_name='', my_record_id=0,
                     media=None):
        """Actual Sending of the sms"""
        sms_account = self.env['sms.account'].search([('id', '=', sms_gateway_id)])

        # format the from number before sending
        format_from = from_number
        if " " in format_from: format_from.replace(" ", "")

        # format the to number before sending
        format_to = []
        format_to.append(str(to_number.replace(" ", "")))

        media_url = ""
        # Create an attachment for the mms now since we need a url now
        if media:
            attachment_id = self.env['ir.attachment'].sudo().create(
                {'name': 'mms ' + str(my_record_id), 'type': 'binary', 'datas': media, 'public': True})
            media_url = request.httprequest.host_url + "web/image/" + str(attachment_id.id) + "/media." + \
                        attachment_id.mimetype.split("/")[1]

            # Force the creation of the new attachment before you make the request
            self.env.cr.commit()  # all good, we commit

        # send the sms/mms
        base_url = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')])[0].value
        payload = {
            # 'senderAddress': format_from.encode('utf-8'),
            'recipientAddressList': format_to,
            'messageContent': sms_content.encode('Latin1'),
            'maxSmsPerMessage': 1
                   }

        if media:
            payload['MediaUrl'] = media_url

        response_string = requests.post(
            "https://api.websms.com/rest/smsmessaging/simple",
            data=payload, auth=(str(sms_account.websms_auth_username), str(sms_account.websms_auth_passwd)))

        # Analyse the reponse string and determine if it sent successfully other wise return a human readable error message
        responses = response_string.content.split("&")
        human_read_error = ""
        statuscode = "failed"
        response_string = ""
        sms_gateway_message_id = ""
        my_sms_response = sms_response()
        for response in responses:
            single_response = response.split("=")
            if single_response[0] == "statusCode":
                if single_response[1] == "2000":
                    statuscode = "successful"
            if single_response[0] == "statusMessage":
                response_string = single_response[1]
                if statuscode != "successful":
                    human_read_error = single_response[1]
            if single_response[0] == "transferId":
                sms_gateway_message_id = single_response[1]
        my_sms_response.delivary_state = statuscode
        my_sms_response.response_string = response_string
        my_sms_response.human_read_error = human_read_error
        my_sms_response.message_id = sms_gateway_message_id
        return my_sms_response

    def check_messages(self, account_id, message_id=""):
        """Checks for any new messages or if the message id is specified get only that message"""
        raise NotImplementedError("Method not implemented.")

    def _add_message(self, sms_message, account_id):
        """Adds the new sms to the system"""
        raise NotImplementedError("Method not implemented.")

    def delivary_receipt(self, account_sid, message_id):
        """Updates the sms message when it is successfully received by the mobile phone"""
        raise NotImplementedError("Method not implemented.")

class SmsAccountWebsms(models.Model):
    _inherit = "sms.account"
    _description = "Adds the Websms specfic gateway settings to the sms gateway accounts"

    websms_auth_username = fields.Char(string='Auth Username')
    websms_auth_passwd = fields.Char(string='Auth Password')
    websms_last_check_date = fields.Datetime(string="Last Check Date")

    @api.one
    def websms_quick_setup(self):
        """Configures your Websms account so inbound messages point to your server, also adds mobile numbers to the system"""
        raise NotImplementedError("Method not implemented.")
