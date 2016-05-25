import flask.ext.restful as restful
import flask.ext.login as login

from flask.ext.restful import reqparse
from flask import g

from common.models import Credential, Account
from common.utils import (
        email_type,
        phone_type,
        md5_hashed_type,
    )
from common.error import (
        AtLeastOneOfArguments,
        CredentialNotFound,
        PasswordIncorrect,
    )

class Login(restful.Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid')
        parser.add_argument('name')
        parser.add_argument('email', type=email_type)
        parser.add_argument('phone', type=phone_type)
        parser.add_argument('passwd', type=md5_hashed_type, default="")
        args = parser.parse_args()

        account = None

        if args['uid']:
            account = Account.query.get(args['uid'])
        else:
            cred_type = \
                'name'  if args['name' ] else \
                'email' if args['email'] else \
                'phone' if args['phone'] else ''
            cred = Credential.query.get(
                    (cred_type, args[cred_type]))
            if not cred.account:
                raise CredentialNotFound(cred_type, args[cred_type]);
            account = cred.account

        if not account:
            raise AtLeastOneOfArguments(['uid', 'name', 'email', 'phone'])

        if account.passwd.lower() != args['passwd'].lower():
            raise PasswordIncorrect()

        login.login_user(account)

        return { "uid": account.uid }

Entry = Login

