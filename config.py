from dotenv import load_dotenv
import os
load_dotenv()
class Config:
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')  
    db_port = os.getenv('DB_PORT')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    from_email=os.getenv('FROM_EMAIL')
    email_app_password=os.getenv('EMAL_APP_PASSWORD')

class emailTemplates:
    def send_otp_template(otp:int,username:str):
        template = f"""hi {username},
        welcome to our **SNS**.
        Your OTP is: {otp}.
        Please use this OTP to complete your verification process.
        this OTP is valid for 5 minutes. If you did not request this OTP, please ignore this email.
        best regards,
        SNS Team
        """
        return template
    def reset_password_template(username:str,reset_link:str,time:int):
        template = f"""hi {username},
        welcome to our **SNS**.
        Please click the link below to reset your password:
        {reset_link}
        this link is valid for {time} minutes. If you did not request this password reset, please ignore this email.
        please do not share this link with anyone else.
        best regards,
        SNS Team
        """
        return template