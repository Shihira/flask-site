import flask.ext.restful as restful
import flask.ext.login as login

from flask.ext.restful import reqparse
from common.globals import loginmgr, db
from common.models.user import Credential
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
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('email', type=email_type)
        parser.add_argument('phone', type=phone_type)
        parser.add_argument('passwd', type=md5_hashed_type, default="")
        args = parser.parse_args()

        cred_type = \
            'name'  if args['name' ] else \
            'email' if args['email'] else \
            'phone' if args['phone'] else ''

        if not cred_type:
            raise AtLeastOneOfArguments(['name', 'email', 'phone'])

        cred = db.session.query(Credential).get((cred_type, args[cred_type]))

        if not cred.account:
            raise CredentialNotFound(cred_type, args[cred_type]);

        account = cred.account
        if account.passwd.lower() != args['passwd'].lower():
            raise PasswordIncorrect()

        login.login_user(account)

        return { "uid": account.uid }

Entry = Login

