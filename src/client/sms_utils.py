import africastalking

# TODO: Initialize Africa's Talking

africastalking.initialize(
    username='sandbox',
    api_key=''
)

sms = africastalking.SMS

class send_sms():

    def __init__(self):
        self.sms = africastalking.SMS
    def sending(self):
            # Set the numbers in international format
            recipients = ["+2348020920855"]
            # Set your message
            message = "Hey AT Ninja!";
            # Set your shortCode or senderId
            sender = "Test123"
            try:
                response = self.sms.send(message, recipients, sender)
                print (response)
            except Exception as e:
                print (f'Houston, we have a problem: {e}')
