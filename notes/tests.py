from django.test import TestCase
import requests
import json
import pytest
# from fundoonotes.settings import BASE_URL
from fundoonotes.fundoonotes.settings import BASE_URL

with open("test.json") as f:
    data = json.load(f)




class TestNote:

    def test_note_post1(self):
        url = BASE_URL + (data[0]['urls']['NoteData'])
        input = data[0]['notepost1']
        response = requests.post(url=url, data=input)
        assert response.status_code == 200




























    def test_note_post2(self):
        url = BASE_URL + (data[0]['urls']['NoteData'])
        input = data[0]['notepost2']
        response = requests.post(url=url, data=input, headers=headers)
        assert response.status_code == 200

    def test_note_post3(self):
        url = BASE_URL + (data[0]['urls']['NoteData'])
        input = data[0]['notepost3']
        response = requests.post(url=url, data=input, headers=headers)
        assert response.status_code == 200

    def test_note_post4(self):
        url = BASE_URL + (data[0]['urls']['NoteData'])
        input = data[0]['notepost4']
        response = requests.post(url=url, data=input, headers=headers)
        assert response.status_code == 400

    def test_note_get1(self):
        url = BASE_URL + (data[0]['urls']['NoteUpdate']) + "/" + (data[0]['noteget1']['note_id'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 400

    def test_note_get2(self):
        url = BASE_URL + (data[0]['urls']['NoteUpdate']) + "/" + (data[0]['noteget2']['note_id'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 404

    def test_note_get3(self):
        url = BASE_URL + (data[0]['urls']['NoteUpdate']) + "/" + (data[0]['noteget3']['note_id'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 200

    def test_note_delete1(self):
        url = BASE_URL + (data[0]['urls']['NoteUpdate']) + "/" + (data[0]['notedelete1']['note_id'])
        response = requests.delete(url=url, headers=headers)
        assert response.status_code == 400

    def test_note_delete2(self):
        url = BASE_URL + (data[0]['urls']['NoteUpdate']) + "/" + (data[0]['notedelete2']['note_id'])
        response = requests.delete(url=url, headers=headers)
        assert response.status_code == 404

    def test_note_delete3(self):
        url = BASE_URL + (data[0]['urls']['NoteUpdate']) + "/" + (data[0]['notedelete3']['note_id'])
        response = requests.delete(url=url, headers=headers)
        assert response.status_code == 200

    #
    def test_note_put1(self):
        url = BASE_URL + (data[0]['urls']['NoteUpdate']) + "/" + (data[0]['noteput1']['note_id'])
        input = data[0]['noteputdata1']
        response = requests.put(url=url, data=input, headers=headers)
        assert response.status_code == 400

    def test_note_put2(self):
        url = BASE_URL + (data[0]['urls']['updatenote']) + "/" + (data[0]['noteput2']['note_id'])
        input = data[0]['noteputdata1']
        response = requests.put(url=url, data=input, headers=headers)
        assert response.status_code == 404

    #
    def test_note_put3(self):
        url = BASE_URL + (data[0]['urls']['NoteUpdate']) + "/" + (data[0]['noteput3']['note_id'])
        input = data[0]['noteputdata1']
        response = requests.put(url=url, data=input, headers=headers)
        assert response.status_code == 400


class TestLabel:

    def test_label_get1(self):
        url = BASE_URL + (data[0]['urls']['LabelsCreate'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 200

    def test_label_get2(self):
        url = BASE_URL + (data[0]['urls']['LabelsCreate'])
        input = data[0]['labelget2']['label_id']
        response = requests.get(url=url, data=input, headers=headers)
        assert response.status_code == 200

    def test_label_put1(self):
        url = BASE_URL + (data[0]['urls']['LabelsCreate']) + "/" + (data[0]['labelget2']['label_id'])
        input = data[0]['labelput2']
        response = requests.put(url=url, data=input, headers=headers)
        assert response.status_code == 200


class TestTrash:
    def test_trash_get1(self):
        url = BASE_URL + (data[0]['urls']['Trash'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 200

    def test_trash_get2(self):
        url = BASE_URL + (data[0]['urls']['Trash'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 404


class TestArchieve:
    def test_archieve_get1(self):
        url = BASE_URL + (data[0]['urls']['Archive'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 200

    def test_archieve_get2(self):
        url = BASE_URL + (data[0]['urls']['Archive'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 404


class TestReminder:
    def test_reminder_get1(self):
        url = BASE_URL + (data[0]['urls']['Remider'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 200

    def test_reminder_get2(self):
        url = BASE_URL + (data[0]['urls']['Remider'])
        response = requests.get(url=url, headers=headers)
        assert response.status_code == 404
