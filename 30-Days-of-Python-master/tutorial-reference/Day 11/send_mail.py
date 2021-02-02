import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from templates import Template
# environment variables
username = 'hungrypy@gmail.com'
password = '<your password>'

class Emailer():
    subject = ""
    context = {}
    to_emails = []
    has_html = False
    test_send = False
    from_email  = 'Hungry Py <hungrypy@gmail.com>'
    template_html = None
    template_name = None
    
    def __init__(self, subject="", template_name=None, context={}, template_html=None, to_emails=None, test_send=False):
        if template_name == None and template_name == None:
            raise Exception("You must set a template")
        assert isinstance(to_emails, list)
        self.to_emails = to_emails
        self.subject = subject
        if template_html != None:
            self.has_html = True
            self.template_html = template_html
        self.template_name = template_name
        self.context = context
        self.test_send = test_send
    
    def format_msg(self):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_email
        msg['To'] = ", ".join(self.to_emails)
        msg['Subject'] = self.subject

        if self.template_name != None:
            tmpl_str = Template(template_name=self.template_name, context=self.context)
            txt_part = MIMEText(tmpl_str.render(), 'plain')
            print(txt_part)
            msg.attach(txt_part)
        if self.template_html != None:
            tmpl_str = Template(template_name=self.template_html, context=self.context)
            html_part = MIMEText(tmpl_str.render(), 'html')
            print(html_part)
            msg.attach(html_part)
        msg_str = msg.as_string()
        return msg_str

    def send(self):
        msg = self.format_msg()
        # login to my smtp server
        did_send = False
        if not self.test_send:
            with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
                server.ehlo()
                server.starttls()
                server.login(username, password)
                try:
                    server.sendmail(from_email, to_emails, msg_str)
                    did_send = True
                except:
                    did_send = False
        return did_send
    # with smtplib.SMTP() as server:
    #     server.login()
    #     pass