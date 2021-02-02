from flask import Blueprint  
main=Blueprint('main',__name__)  
from . import views,errors 
@main.app_context_processor
def admin_email():
    email='879651072@qq.com'
    return dict(email='879651072@qq.com')
