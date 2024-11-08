import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from django.contrib.messages import get_messages
from django.contrib import auth


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
    return user


@pytest.mark.django_db
class TestAuthSignupView:
    def test_signup_success(self, client):
        url = reverse('users:signup')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'confirm-password': 'newpassword123'
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert response.url == '/signin'
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_signup_missing_fields(self, client):
        url = reverse('users:signup')
        data = {
            'email': '',
            'password': '',
            'confirm-password': ''
        }
        response = client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        assert any("All fields are required." in str(message) for message in messages)
        assert response.status_code == 200

    def test_signup_password_mismatch(self, client):
        url = reverse('users:signup')
        data = {
            'email': 'user@example.com',
            'password': 'password123',
            'confirm-password': 'password456'
        }
        response = client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        assert any("Passwords do not match." in str(message) for message in messages)
        assert response.status_code == 200

    def test_signup_password_too_short(self, client):
        url = reverse('users:signup')
        data = {
            'email': 'user@example.com',
            'password': 'short',
            'confirm-password': 'short'
        }
        response = client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        assert any("Password must be at least 8 characters." in str(message) for message in messages)
        assert response.status_code == 200

    def test_signup_email_already_in_use(self, client, user):
        url = reverse('users:signup')
        data = {
            'email': user.email,
            'password': 'password123',
            'confirm-password': 'password123'
        }
        response = client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        assert any("Email is already in use." in str(message) for message in messages)
        assert response.status_code == 200


@pytest.mark.django_db
class TestAuthSigninView:
    def test_signin_success(self, client, user):
        url = reverse('users:signin')
        data = {
            'email': user.username,
            'password': 'password'
        }
        response = client.post(url, data)
        assert response.status_code == 302

        user_from_session = auth.get_user(client)
        assert user_from_session.is_authenticated
        assert user_from_session.email == user.email

    def test_signin_invalid_credentials(self, client):
        url = reverse('users:signin')
        data = {
            'email': 'invalid@example.com',
            'password': 'wrongpassword'
        }
        response = client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        assert any("Invalid email or password." in str(message) for message in messages)
        assert response.status_code == 200

    def test_signin_missing_fields(self, client):
        url = reverse('users:signin')
        data = {
            'email': '',
            'password': ''
        }
        response = client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        assert any("Both email and password are required." in str(message) for message in messages)
        assert response.status_code == 200


class TestAuthLogoutView:
    def test_logout(self, client, user):
        client.login(username=user.username, password='password')
        url = reverse('users:logout')
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == '/signin/'
        assert '_auth_user_id' not in client.session
