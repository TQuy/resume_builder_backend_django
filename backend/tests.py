import json
import re
from django.db import IntegrityError
from django.test import TestCase
from backend.models import Resume
from django.db import transaction
from authentication.models import User
from authentication.tests import UserTestCase
from rest_framework.test import APIClient
from backend.const import SAMPLE_RESUME
from urllib.parse import urlencode


# Create your tests here.


class ResumeTestCase(TestCase):
    def setUp(self):
        self.username = 'quynt'
        self.password = '1'
        self.content = json.dumps(SAMPLE_RESUME)

    def test_resume_model(self):
        # create new account
        user = User.objects.create_user(
            username=self.username,
            password=self.password)
        self.assertEqual(User.objects.count(), 1)

        Resume.objects.create(
            name='first_resume',
            content=self.content,
            user=user
        )
        self.assertEqual(Resume.objects.count(), 1)
        # create resume with existed name
        with self.assertRaises(IntegrityError) as err:
            with transaction.atomic():
                Resume.objects.create(
                    name='first_resume',
                    content=self.content,
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
            content=self.content,
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
        response = self.create_resume("first_resume", self.content, token)
        self.assertEqual(response.status_code, 201)
        # check if new resume is added
        self.assertEqual(created_user.resume_set.count(), 1)
        # create the existed one
        response = self.create_resume("first_resume", self.content, token)
        self.assertEqual(response.status_code, 200)
        # modify the existed one
        response = self.create_resume("first_resume", self.content, token)
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
        response = self.create_resume("first_resume", self.content, token)
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
        input_name = "first_resume"
        response = self.create_resume(input_name, self.content, token)
        resume_name = json.loads(response.content)['resume']['name']
        self.assertEqual(response.status_code, 201)
        # read resume
        response = self.read_resume(token, resume_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            input_name, json.loads(
                response.content)['resume']['name'])
        # delete resume, then read again
        created_user.resume_set.filter(name=resume_name).delete()
        response = self.read_resume(token, resume_name)
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
        input_name = "first_resume"
        response = self.create_resume(input_name, self.content, token)
        resume_name = json.loads(response.content)['resume']['name']
        self.assertEqual(response.status_code, 201)
        current_resume_quantity = created_user.resume_set.count()
        # delete resume
        response = self.delete_resume(token, resume_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            current_resume_quantity - 1,
            created_user.resume_set.count())
        # delte non-existed resume
        response = self.delete_resume(token, resume_name)
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
    def read_resume(token: str, name: str):
        client = APIClient()
        response = client.get(
            f"/resumes/{name}", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        return response

    @staticmethod
    def delete_resume(token: str, name: str):
        client = APIClient()
        data = {"name": name}
        response = client.delete(
            f"/resumes/",
            **{"HTTP_AUTHORIZATION": f"Bearer {token}", "QUERY_STRING": urlencode(data)},

        )
        return response
