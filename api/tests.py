import datetime
import json
import pytz
import shutil
from unittest import mock
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from tickets.models import Ticket, Comment, Attachment

TEST_DIR = 'test_data'


class TicketsTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path("api/", include("api.urls")),
    ]

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="test123",
                                                         email="test@gmail.com", first_name="Test",
                                                         last_name="Testtest")
        self.second_user = get_user_model().objects.create_user(username="test2", password="test123",
                                                                email="test2@gmail.com", first_name="Test2",
                                                                last_name="Testtest2")
        self.mocked = datetime.datetime(2022, 9, 15, 0, 0, 0, tzinfo=pytz.utc)
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            self.ticket_assigned = Ticket.objects.create(title="New ticket", description="Test", status=1, priority=1,
                                                         assigned=self.user, created=self.mocked, created_by=self.user)
            self.ticket_notassigned = Ticket.objects.create(title="New ticket", description="Test", status=1,
                                                            priority=1, created=self.mocked, created_by=self.user)
        self.client.login(username="test", password="test123")

    def test_ticket_create_with_assign_authenticated(self):
        url = reverse("ticket-list")
        response = self.client.post(url, {"title": "New ticket", "description": "Test", "status": 1, "priority": 1,
                                          "assigned": "test"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_ticket_create_without_assign_authenticated(self):
        url = reverse("ticket-list")
        response = self.client.post(url, {"title": "New ticket 2", "description": "Test 2", "status": 1, "priority": 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_ticket_detail_retrieve_authenticated(self):
        url = reverse("ticket-detail", kwargs={"pk": self.ticket_assigned.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "New ticket")

    def test_ticket_update_with_assign_authenticated(self):
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            url = reverse("ticket-detail", kwargs={"pk": self.ticket_assigned.pk})
            response = self.client.put(url, {"title": "New ticket update", "description": "Test update", "status": 2,
                                             "priority": 3, "assigned": "test2", "created": self.mocked, "modified": self.mocked})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(json.loads(response.content), {"title": "New ticket update",
                                                            "description": "Test update", "status": 2,
                                                            "priority": 3, "assigned": "test2", "created": datetime.datetime.isoformat(self.mocked),
                                                            "modified": datetime.datetime.isoformat(self.mocked), "created_by": self.user.username})

    def test_ticket_update_without_assign_authenticated(self):
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            url = reverse("ticket-detail", kwargs={"pk": self.ticket_notassigned.pk})
            response = self.client.put(url, {"title": "New ticket update", "description": "Test update", "status": 2,
                                             "priority": 3, "created": self.mocked, "modified": self.mocked})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(json.loads(response.content), {"title": "New ticket update",
                                                            "description": "Test update", "status": 2,
                                                            "priority": 3, "created": datetime.datetime.isoformat(self.mocked),
                                                            "modified": datetime.datetime.isoformat(self.mocked), "created_by": self.user.username})

    def test_ticket_list_authenticated(self):
        url = reverse("ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_ticket_delete_authenticated(self):
        url = reverse("ticket-detail", kwargs={"pk": self.ticket_assigned.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_ticket_create_with_assign_no_authenticated(self):
        self.client.logout()
        url = reverse("ticket-list")
        response = self.client.post(url, {"title": "New ticket", "description": "Test", "status": 1, "priority": 1,
                                          "assigned": "test"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_create_without_assign_no_authenticated(self):
        self.client.logout()
        url = reverse("ticket-list")
        response = self.client.post(url, {"title": "New ticket 2", "description": "Test 2", "status": 1, "priority": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_detail_retrieve_no_authenticated(self):
        self.client.logout()
        url = reverse("ticket-detail", kwargs={"pk": self.ticket_assigned.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_update_with_assign_no_authenticated(self):
        self.client.logout()
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            url = reverse("ticket-detail", kwargs={"pk": self.ticket_assigned.pk})
            response = self.client.put(url, {"title": "New ticket update", "description": "Test update", "status": 2,
                                             "priority": 3, "assigned": "test2", "created": self.mocked, "modified": self.mocked})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_update_without_assign_no_authenticated(self):
        self.client.logout()
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            url = reverse("ticket-detail", kwargs={"pk": self.ticket_notassigned.pk})
            response = self.client.put(url, {"title": "New ticket update", "description": "Test update", "status": 2,
                                             "priority": 3, "created": self.mocked, "modified": self.mocked})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_list_no_authenticated(self):
        self.client.logout()
        url = reverse("ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_delete_no_authenticated(self):
        self.client.logout()
        url = reverse("ticket-detail", kwargs={"pk": self.ticket_assigned.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentsTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path("api/", include("api.urls")),
    ]

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="test123",
                                                         email="test@gmail.com", first_name="Test",
                                                         last_name="Testtest")
        self.second_user = get_user_model().objects.create_user(username="test2", password="test123",
                                                                email="test2@gmail.com", first_name="Test2",
                                                                last_name="Testtest2")
        self.mocked = datetime.datetime(2022, 9, 15, 0, 0, 0, tzinfo=pytz.utc)
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            self.ticket = Ticket.objects.create(title="New ticket", description="Test", status=1, priority=1,
                                                assigned=self.user, created=self.mocked, created_by=self.user)
            self.comment = Comment.objects.create(ticket=self.ticket, description="Test comment",
                                                  created=self.mocked, author=self.user)
        self.client.login(username="test", password="test123")

    def test_comment_create_authenticated(self):
        url = reverse("comment-list")
        response = self.client.post(url, {"ticket": self.ticket.pk, "description": "New comment"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_detail_retrieve_authenticated(self):
        url = reverse("comment-detail", kwargs={"pk": self.comment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Test comment")

    def test_comment_update_authenticated(self):
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            url = reverse("comment-detail", kwargs={"pk": self.comment.pk})
            response = self.client.put(url, {"description": "Update comment", "created": self.mocked,
                                             "modified": self.mocked})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(json.loads(response.content), {"ticket": self.ticket,
                                                            "description": "Update comment",
                                                            "created": datetime.datetime.isoformat(self.mocked),
                                                            "modified": datetime.datetime.isoformat(self.mocked),
                                                            "author": self.user.username})

    def test_comment_list_authenticated(self):
        url = reverse("comment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_comment_delete_authenticated(self):
        url = reverse("comment-detail", kwargs={"pk": self.comment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comment_create_no_authenticated(self):
        self.client.logout()
        url = reverse("comment-list")
        response = self.client.post(url, {"ticket": self.ticket, "description": "New comment"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_detail_retrieve_no_authenticated(self):
        self.client.logout()
        url = reverse("comment-detail", kwargs={"pk": self.comment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_update_no_authenticated(self):
        self.client.logout()
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            url = reverse("comment-detail", kwargs={"pk": self.comment.pk})
            response = self.client.put(url, {"description": "Update comment", "created": self.mocked,
                                             "modified": self.mocked})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_list_no_authenticated(self):
        self.client.logout()
        url = reverse("comment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_delete_no_authenticated(self):
        self.client.logout()
        url = reverse("comment-detail", kwargs={"pk": self.comment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AttachmentsTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path("api/", include("api.urls")),
    ]

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="test123",
                                                         email="test@gmail.com", first_name="Test",
                                                         last_name="Testtest")
        self.file = SimpleUploadedFile("test.txt", b"abc")
        self.mocked = datetime.datetime(2022, 9, 15, 0, 0, 0, tzinfo=pytz.utc)
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=self.mocked)):
            self.ticket = Ticket.objects.create(title="New ticket", description="Test", status=1, priority=1,
                                                assigned=self.user, created=self.mocked, created_by=self.user)
            self.attachment = Attachment.objects.create(ticket=self.ticket, file=self.file,
                                                        created=self.mocked, author=self.user)
        self.client.login(username="test", password="test123")
        self.file.seek(0)

    def tearDown(self):
        print("\nDeleting temporary files...\n")
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_attachment_create_authenticated(self):
        url = reverse("attachment-list")
        response = self.client.post(url, {"ticket": self.ticket.pk, "file": self.file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_attachment_detail_retrieve_authenticated(self):
        url = reverse("attachment-detail", kwargs={"pk": self.attachment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["file"], "tickets/1/test.txt")

    def test_attachment_list_authenticated(self):
        url = reverse("attachment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_attachment_delete_authenticated(self):
        url = reverse("attachment-detail", kwargs={"pk": self.attachment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_attachment_create_no_authenticated(self):
        self.client.logout()
        url = reverse("attachment-list")
        response = self.client.post(url, {"ticket": self.ticket.pk, "file": self.file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_attachment_detail_retrieve_no_authenticated(self):
        self.client.logout()
        url = reverse("attachment-detail", kwargs={"pk": self.attachment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_attachment_list_no_authenticated(self):
        self.client.logout()
        url = reverse("attachment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_attachment_delete_no_authenticated(self):
        self.client.logout()
        url = reverse("attachment-detail", kwargs={"pk": self.attachment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
