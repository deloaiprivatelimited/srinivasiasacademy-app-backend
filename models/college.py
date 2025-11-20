from mongoengine import Document, StringField, DictField, ValidationError

class College(Document):
    college_name = StringField(required=True)
    gstin = StringField(required=True, unique=True, regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
    college_id = StringField(required=True, unique=True)
    address = StringField(required=True)
    coordinator_contact_cards = DictField()  # You can enhance this further
    token = StringField()
    payment_info = DictField()
    subscription_details = DictField()
    recharge_token = StringField()

    meta = {'collection': 'colleges'}

    def to_json(self):
        return {
            "id": str(self.id),
            "college_name": self.college_name,
            "gstin": self.gstin,
            "college_id": self.college_id,
            "address": self.address,
            "coordinator_contact_cards": self.coordinator_contact_cards,
            "token": self.token,
            "payment_info": self.payment_info,
            "subscription_details": self.subscription_details,
            "recharge_token": self.recharge_token
        }
