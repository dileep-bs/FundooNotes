from django.urls import reverse
from .models import Notes, Label
from django.test import TestCase
from fundoonotes.settings import BASE_URL
header = {
    'HTTP_AUTHORIZATION': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTc0Mzk4NjEyLCJqdGkiOiJjMWYzZTE4Mjc4Mzc0MWVhODM0MTRlYjViMjMwZGJiZiIsInVzZXJfaWQiOjF9.5AkRWKN8wpeLMOZsGWgSdomDv_GdKsWibwZCv-pUjeU"}

class ModelsTest(TestCase):

    def test_note_string_representation1(self):
        entry = Notes(note="title one")
        self.assertEqual(str(entry), entry.note)

    def test_note_string_representation2(self):
        entry = Notes(title="title one")
        self.assertEqual(str(entry), "")

    def test_note_equal2(self):
        note1 = Notes(note="note 1st")
        note2 = Notes(note="second note 2nd")
        self.assertFalse(note1 == note2, True)

    def label_note_string_representation1(self):
        entry=Label(label='my label1')
        self.assertEqual(str(entry),entry.name)

    def label_note_string_representation2(self):
        entry=Label(label='my new label')
        self.assertEqual(str(entry),entry.name)

class NoteTest(TestCase):

    def test_note_getall1(self):
        url = BASE_URL + reverse('notes')
        resp = self.client.get(url, content_type='application/json', **header)
        self.assertEqual(resp.status_code, 404)

    def test_note_get1(self):
        url = BASE_URL + reverse('note_update', args=[1])
        resp = self.client.get(url, content_type='application/json', **header)
        self.assertEqual(resp.status_code, 404)

    def test_note_get2(self):
        url = BASE_URL + reverse('note_update', args=["fbv"])
        resp = self.client.get(url, content_type='application/json', **header)
        self.assertEqual(resp.status_code, 404)
