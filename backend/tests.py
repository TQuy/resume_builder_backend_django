import json
import re
from urllib import response
from django.db import IntegrityError
from django.test import TestCase
from backend.models import Resume
from django.db import transaction
from authentication.models import User
from authentication.tests import UserTestCase
from rest_framework.test import APIClient

# Create your tests here.


class ResumeTestCase(TestCase):
    def setUp(self):
        self.username = 'quynt'
        self.password = '1'

    def test_resume_model(self):
        # create new account
        user = User.objects.create_user(
            username=self.username,
            password=self.password)
        self.assertEqual(User.objects.count(), 1)

        Resume.objects.create(
            name='first_resume',
            content='hello world!',
            user=user
        )
        self.assertEqual(Resume.objects.count(), 1)
        # create the existed one
        with self.assertRaises(IntegrityError) as err:
            with transaction.atomic():
                Resume.objects.create(
                    name='first_resume',
                    content='hi world!',
                    user=user
                )
        self.assertTrue(
            re.search(
                r"unique", str(err.exception), re.IGNORECASE
            )
        )
        # create new
        Resume.objects.create(
            name='second_resume',
            content='hi world!',
            user=user
        )
        self.assertEqual(Resume.objects.count(), 2)

    def test_put_resume(self):
        # create user
        UserTestCase.register_user(self.username, self.password)
        self.assertEqual(User.objects.count(), 1)
        _, token = UserTestCase.login_user(self.username, self.password)
        self.assertTrue(isinstance(token, str))
        self.assertTrue(len(token) > 0)

        created_user = User.objects.get(username=self.username)
        response = self.create_resume("first_resume", "hello world!", token)
        self.assertEqual(response.status_code, 201)
        # check if new resume is added
        self.assertEqual(created_user.resume_set.count(), 1)
        # create the existed one
        response = self.create_resume("first_resume", "hello world!", token)
        self.assertEqual(response.status_code, 200)
        # modify the existed one
        response = self.create_resume("first_resume", "hi world!", token)
        self.assertEqual(response.status_code, 200)

    def test_list_resume(self):
        # create user
        UserTestCase.register_user(self.username, self.password)
        self.assertEqual(User.objects.count(), 1)
        _, token = UserTestCase.login_user(self.username, self.password)
        self.assertTrue(isinstance(token, str))
        self.assertTrue(len(token) > 0)
        # create resume
        created_user = User.objects.get(username=self.username)
        response = self.create_resume("first_resume", "hello world!", token)
        self.assertEqual(response.status_code, 201)
        # list_resume
        response = self.list_resume(token)
        self.assertEqual(response.status_code, 200)
        resume_list = json.loads(response.content).get('resumes')
        self.assertEqual(len(resume_list), created_user.resume_set.count())
        # delete one resume
        created_user.resume_set.first().delete()
        response = self.list_resume(token)
        self.assertEqual(response.status_code, 200)
        resume_list = json.loads(response.content).get('resumes')
        self.assertEqual(len(resume_list), created_user.resume_set.count())

    def test_read_resume(self):
        # create user
        UserTestCase.register_user(self.username, self.password)
        self.assertEqual(User.objects.count(), 1)
        _, token = UserTestCase.login_user(self.username, self.password)
        self.assertTrue(isinstance(token, str))
        self.assertTrue(len(token) > 0)
        # create resume
        created_user = User.objects.get(username=self.username)
        response = self.create_resume("first_resume", "hello world!", token)
        resume_id = json.loads(response.content)['resume']['id']
        self.assertEqual(response.status_code, 201)
        # read resume
        response = self.read_resume(token, resume_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            resume_id, json.loads(
                response.content)['resume']['id'])
        # delete resume, then read again
        created_user.resume_set.filter(pk=resume_id).delete()
        response = self.read_resume(token, resume_id)
        self.assertEqual(response.status_code, 404)

    def test_delete_resume(self):
        # create user
        UserTestCase.register_user(self.username, self.password)
        self.assertEqual(User.objects.count(), 1)
        _, token = UserTestCase.login_user(self.username, self.password)
        self.assertTrue(isinstance(token, str))
        self.assertTrue(len(token) > 0)
        # create resume
        created_user = User.objects.get(username=self.username)
        response = self.create_resume("first_resume", "hello world!", token)
        resume_id = json.loads(response.content)['resume']['id']
        self.assertEqual(response.status_code, 201)
        current_resume_quantity = created_user.resume_set.count()
        # delte resume
        response = self.delete_resume(token, resume_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            current_resume_quantity - 1,
            created_user.resume_set.count())
        # delte non-existed resume
        response = self.delete_resume(token, resume_id)
        self.assertEqual(response.status_code, 204)

    @staticmethod
    def create_resume(name: str, content: str, token: str):
        client = APIClient()
        response = client.put('/resumes/', data={
            "name": name,
            "content": content
        }, format='json', **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        return response

    @staticmethod
    def list_resume(token: str):
        client = APIClient()
        response = client.get('/resumes/',
                              **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        return response

    @staticmethod
    def read_resume(token: str, id: int):
        client = APIClient()
        response = client.get(
            f"/resumes/{id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        return response

    @staticmethod
    def delete_resume(token: str, id: int):
        client = APIClient()
        response = client.delete(
            f"/resumes/{id}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        return response
