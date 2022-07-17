from django.db import IntegrityError
from django.test import TestCase
from authentication.models import User
from django.contrib.auth.hashers import check_password
import re
from django.db import transaction
from rest_framework.test import APIClient
import json


class UserTestCase(TestCase):
    def setUp(self):
        self.username = 'quynt'
        self.password = '1'

    def test_user_model(self):
        User.objects.create_user(
            username=self.username,
            password=self.password)
        # check if new record is inserted
        self.assertEqual(User.objects.count(), 1)
        # check if unique related error is raised
        with self.assertRaises(IntegrityError) as err:
            with transaction.atomic():
                User.objects.create_user(
                    username=self.username, password=self.password)
        self.assertTrue(
            re.match(
                r"unique", str(
                    err.exception), flags=re.IGNORECASE))

        another_username = 'quynt1'
        user2 = User.objects.create_user(
            username=another_username,
            password=self.password)
        self.assertEqual(User.objects.count(), 2)

        user2.delete()
        self.assertEqual(User.objects.count(), 1)

    @staticmethod
    def register_user(username, password):
        client = APIClient()
        response = client.post('/auth/register', data={
            "username": username,
            "password": password
        }, format='json')
        return client, response

    def test_register_user(self):
        _, response = self.register_user(self.username, self.password)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

        created_user = User.objects.first()
        # check if password is hashed
        self.assertTrue(check_password(self.password, created_user.password))

        _, response = self.register_user(self.username, self.password)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content).get(
            "error"), "username has already been registered")

    def test_login_user(self):
        self.register_user(self.username, self.password)
        response, token = self.login_user(self.username, self.password)
        self.assertEqual(response.status_code, 200)
        # check that token exist in response
        self.assertTrue(isinstance(token, str))
        self.assertTrue(len(token) > 0)

        response, _ = self.login_user(self.username, 'hello')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content).get(
            "error"), "Authentication failed!")

    @staticmethod
    def login_user(username, password):
        client = APIClient()
        response = client.post('/auth/login', data={
            "username": username,
            "password": password
        }, format='json')
        token = json.loads(response.content).get('token')
        return response, token
