import unittest
import werkzeug
import hashlib
import json

from flask import current_app, url_for, session

from common.models import (
        Account,
        Credential,
    )
from common.error import *
from common.utils import ApiTest, test_context

class AuthTest(ApiTest):

    def setUp(self):
        super(AuthTest, self).setUp()

        self.account_1 = Account(
                passwd = hashlib.md5(b"123pass").hexdigest()
            )
        self.account_2 = Account()

        self.dbsess.add(self.account_1)
        self.dbsess.add(self.account_2)
        self.dbsess.flush()
        self.dbsess.add(Credential(
                uid = self.account_1.uid,
                cred_type = 'name',
                cred_value = 'john'
            ))
        self.dbsess.add(Credential(
                uid = self.account_2.uid,
                cred_type = 'name',
                cred_value = 'gump',
            ))
        self.dbsess.add(Credential(
                uid = self.account_2.uid,
                cred_type = 'email',
                cred_value = 'gump@gump.com',
            ))
        self.dbsess.commit()

    @test_context
    def test_create_account(self):
        response = self.client.post(
                path = url_for("api.auth.account"),
                data = { 'name': 'bill' }
            )
        data = self.load_data(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(data["uid"], "[0-9a-z\-]{36}")

    @test_context
    def test_create_duplicated_account(self):
        response = self.client.post(
                path = url_for("api.auth.account"),
                data = { 'name': 'john' }
            )
        data = self.load_data(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertApiError(data, AccountAlreadyExists)

    @test_context
    def test_successful_login_no_password(self):
        response = self.client.post(
                path = url_for("api.auth.login"),
                data = { 'name': 'gump', }
            )
        data = self.load_data(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(data["uid"], "[0-9a-z\-]{36}")
        self.assertEqual(session["user_id"], self.account_2.uid)

    @test_context
    def test_successful_login_with_password(self):
        response = self.client.post(
                path = url_for("api.auth.login"),
                data = {
                    'name': 'john',
                    'passwd': hashlib.md5(b"123pass").hexdigest()
                }
            )
        data = self.load_data(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(data["uid"], "[0-9a-z\-]{36}")
        self.assertEqual(session["user_id"], self.account_1.uid)

    @test_context
    def test_login_password_incorrect(self):
        response = self.client.post(
                path = url_for("api.auth.login"),
                data = {
                    'name': 'john',
                    'passwd': hashlib.md5(b"wrong").hexdigest(),
                }
            )
        data = self.load_data(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertApiError(data, PasswordIncorrect)

    @test_context
    def test_logout_without_having_logged_in(self):
        response = self.client.post(
                path = url_for("api.auth.logout"),
            )
        data = self.load_data(response.data)

        self.assertEqual(response.status_code, 401)

    @test_context
    def test_logout_user(self):
        self.login_user(self.account_1)
        self.assertEqual(session["user_id"], self.account_1.uid)

        response = self.client.post(
                path = url_for("api.auth.logout"),
            )

        self.assertNotIn("user_id", session)


suite = unittest.TestSuite()
suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(AuthTest))

