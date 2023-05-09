from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersManagersTests(TestCase):
    def test_create_user(self):
        email_address = "simple@user.com"
        password = "foo"
        User = get_user_model()
        user = User.objects.create_user(email=email_address, password=password)
        self.assertEqual(user.email, email_address)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password=password)

    def test_create_superuser(self):
        email_address = "super@user.com"
        password = "foo"
        User = get_user_model()
        user = User.objects.create_superuser(email=email_address, password=password)
        self.assertEqual(user.email, email_address)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", password=password, is_superuser=False
            )
