# -*- coding: utf-8 -*-
from datetime import datetime
from urllib import urlencode, quote as quote
import logging
_logger = logging.getLogger(__name__)

from openerp import api, fields, models, tools

class SMSAlarm(models.Model):

    _name = "sms.alarm"
    
    @api.model        
    def send_sms_to_attendees(self,event):
        _logger.error("sms alarm")
        sms_template = self.env['ir.model.data'].get_object('sms_frame_calendar_alarm','sms_calendar_reminder')
        sms_template_attendee = self.env['ir.model.data'].get_object('sms_frame_calendar_alarm','sms_calendar_reminder_attendee')
        
        #Uncomment in v10
        #for attendee in event.attendee_ids:
        #    self.env['sms.template'].send_sms(sms_template_attendee.id, attendee.id)
            
        for attendee in event.partner_ids:
            sms_template.sms_to = attendee.mobile
            self.env['sms.template'].send_sms(sms_template.id, event.id)
