import re

import flask.ext.restful as restful
from flask.ext.restful import reqparse

from common.globals import db
from common.utils import (
        email_type,
        phone_type,
        md5_hashed_type,
    )
import common.models.user as user_models

class Account(restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('email', type=email_type)
        parser.add_argument('phone', type=phone_type)
        parser.add_argument('passwd', type=md5_hashed_type)

        args = parser.parse_args()

        new_account = user_models.Account(
                passwd = args['passwd'],
            )
        db.session.add(new_account)
        db.session.flush()

        new_username = user_models.Credential(
                cred_type = 'name',
                cred_value = args['name'],
                uid = new_account.uid
            )
        db.session.add(new_username)

        if args['email']:
            new_email = user_models.Credential(
                    cred_type = 'email',
                    cred_value = args['email'],
                    uid = new_account.uid
                )
            db.session.add(new_email)

        if args['phone']:
            new_phone = user_models.Credential(
                    cred_type = 'phone',
                    cred_value = args['phone'],
                    uid = new_account.uid
                )
            db.session.add(new_phone)

        db.session.commit()

Entry = Account

