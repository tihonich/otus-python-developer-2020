import unittest
import json
import fields
from store import Store
from time import sleep


TEST_PORT = 10101

def cases(cases_list):
    def deco(func):
        def wrapper(self):
            for case in cases_list:
                func(self, case)

        return wrapper
    return deco


class TestFields(unittest.TestCase):
    @cases([5, dict(), list(), True])
    def test_CharField_validate_incorrect_value(self, value):
        with self.assertRaises(ValueError):
            fields.CharField.validate(fields.CharField(), value)

    def test_CharField_validate_correct_value(self):
        self.assertTrue((fields.CharField.validate(fields.CharField(), '5') is None))

    @cases([5, dict(), 'ab', True])
    def test_ListField_validate_incorrect_value(self, value):
        with self.assertRaises(ValueError):
            fields.ListField.validate(fields.ListField(), value)

    def test_ListField_validate_correct_value(self):
        self.assertTrue(fields.ListField.validate(fields.ListField(), [1, 2, 3]) is None)

    @cases([5, list(), 'ab', True])
    def test_DictField_validate_incorrect_value(self, value):
        with self.assertRaises(ValueError):
            fields.DictField.validate(fields.DictField(), value)

    def test_DictField_validate_correct_value(self):
        self.assertTrue(fields.DictField.validate(fields.DictField(),
                                                  {'name': 'Alexy', 'surname': 'Vassili'}) is None)

    @cases([5, list(), 'ab', True, 'ab.com', 'ab at ab.com'])
    def test_EmailField_validate_incorrect_value(self, value):
        with self.assertRaises(ValueError):
            fields.EmailField.validate(fields.EmailField(), value)

    def test_EmailField_validate_correct_value(self):
        self.assertTrue(fields.EmailField.validate(fields.EmailField(), 'petros@gmail.com') is None)

    @cases([5, list(), 'ab', True, 89632223344, 7963222334, 789632223344,
            '89632223344', '7963222334', '789632223344'])
    def test_PhoneField_validate_incorrect_value(self, value):
        with self.assertRaises(ValueError):
            fields.PhoneField.validate(fields.PhoneField(), value)

    def test_PhoneField_validate_correct_value(self):
        self.assertTrue(fields.PhoneField.validate(fields.PhoneField(), '79637222999') is None)
        self.assertTrue(fields.PhoneField.validate(fields.PhoneField(), 79637222999) is None)

    @cases(['08.05..2003', '08.052003', '08/05/2003', '08:05:2003', '08052003'])
    def test_DateField_validate_incorrect_value(self, value):
        with self.assertRaises(ValueError):
            fields.DateField.validate(fields.DateField(), value)

    def test_DateField_validate_correct_value(self):
        self.assertTrue(fields.DateField.validate(fields.DateField(), '08.05.2003') is None)
        self.assertTrue(fields.DateField.validate(fields.DateField(), '08.05.1920') is None)

    def test_BirthDayField_validate_incorrect_value(self):
        with self.assertRaises(ValueError):
            # > 70 years
            fields.BirthDayField.validate(fields.BirthDayField(), '09.05.1945')

    def test_BirthDayField_validate_correct_value(self):
        self.assertTrue(fields.BirthDayField.validate(fields.BirthDayField(), '09.05.1997') is None)

    def test_GenderField_validate_incorrect_value(self):
        with self.assertRaises(ValueError):
            fields.GenderField.validate(fields.GenderField(), -1)
        with self.assertRaises(ValueError):
            fields.GenderField.validate(fields.GenderField(), 100)

    def test_GenderField_validate_correct_value(self):
        self.assertTrue(fields.GenderField.validate(fields.GenderField(), fields.UNKNOWN) is None)
        self.assertTrue(fields.GenderField.validate(fields.GenderField(), fields.MALE) is None)
        self.assertTrue(fields.GenderField.validate(fields.GenderField(), fields.FEMALE) is None)

    def test_ClientIDsField_validate_incorrect_value(self):
        with self.assertRaises(ValueError):
            # not a List
            fields.ClientIDsField.validate(fields.ClientIDsField(), (1, 2, 3, 4, 5))
        with self.assertRaises(ValueError):
            # not int
            fields.ClientIDsField.validate(fields.ClientIDsField(), (1, 2, 3, 4, '5'))

    def test_ClientIDsField_validate_correct_value(self):
        self.assertTrue(fields.ClientIDsField.validate(fields.ClientIDsField(), [1, 2, 3, 4, 5]) is None)

    def test_ArgumentsField_validate_incorrect_value(self):
        with self.assertRaises(ValueError):
            # non-dict type
            fields.ArgumentsField.validate(fields.ArgumentsField(), [1, 2, 3, 4, 5])

    def test_ArgumentsField_validate_correct_value(self):
        self.assertTrue(fields.ArgumentsField.validate(fields.ArgumentsField(), {"phone": "79175002040",
                                                     "email": "stuv@otus.ru",
                                                     "first_name": "Сергей",
                                                     "last_name": "Костюков",
                                                     "birthday": "01.01.1990",
                                                     "gender": 1}
                                              ) is None)


from server import HOST, PORT
from threading import Thread
from http.server import HTTPServer
from http.client import HTTPConnection
from server import MainHTTPHandler


class TestHTTP(unittest.TestCase):
    host = HOST

    port = TEST_PORT

    headers = {"Content-type": "application/json",
               "Accept": "text/plain"}

    server = None
    thread = None

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer((cls.host, cls.port), MainHTTPHandler)
        cls.thread = Thread(target=cls.server.serve_forever)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def setUp(self):
        print(self.host, self.port)
        self.conn = HTTPConnection(self.host, self.port, timeout=10)

    def tearDown(self):
        self.conn.close()

    def test_online_score(self):
        req = {"account": "horns&hoofs",
               "login": "h&f",
               "method": "online_score",
               "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
               "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
                             "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}
        self.conn.request("POST", "/method/", json.dumps(req), self.headers)
        r = self.conn.getresponse()
        # data = r.read()
        data = json.load(r)
        self.assertIn('code', data)
        self.assertIn('response', data)
        response = data['response']
        self.assertEqual(data['code'], 200)
        self.assertIn('score', response)
        self.assertEqual(type(response['score']), float)

    @cases([{"account": "horns&hoofs",  # empty token
               "login": "h&f",
               "method": "online_score",
               "token": "",
               "arguments": {}},
            {"account": "horns&hoofs",  # invalid token
             "login": "h&f",
             "method": "online_score",
             "token": "sdd",
             "arguments": {}},
            {"account": "horns&hoof",  # broken acc
             "login": "h&f",
             "method": "online_score",
             "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
             "arguments": {}},
            {"account": "",  # empty acc
             "login": "h&f",
             "method": "online_score",
             "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
             "arguments": {}},
            {"account": "horns&hoofs",  # broken login
             "login": "h&",
             "method": "online_score",
             "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
             "arguments": {}},
            {"account": "horns&hoofs",  # empty login
             "login": "",
             "method": "online_score",
             "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
             "arguments": {}},
            {"account": "",
             "login": "",
             "method": "online_score",
             "token": "",
             "arguments": {}},
            {"account": "horns&hoofs",
             "login": "",
             "method": "online_score",
             "token": "",
             "arguments": {}},
            ])
    def test_bad_auth(self, request):
        self.conn.request("POST", "/method/", json.dumps(request), self.headers)
        r = self.conn.getresponse()
        data = json.load(r)
        self.assertIn('code', data)
        self.assertIn('error', data)
        self.assertEqual(data['code'], 403)
        self.assertEqual(data['error'], 'Forbidden')

    def test_unexpected_method(self):
        self.conn.request("GET", "/method/")
        r = self.conn.getresponse()
        data = r.read()
        self.assertEqual(r.status, 501)

    @cases(["/me/", "/", "../../"])
    def test_unexpected_url(self, url):
        req = {"account": "horns&hoofs",
               "login": "h&f",
               "method": "online_score",
               "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
               "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
                             "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}
        self.conn.request("POST", url, json.dumps(req), self.headers)
        r = self.conn.getresponse()
        data = json.load(r)
        self.assertIn('code', data)
        self.assertIn('error', data)
        self.assertEqual(data['code'], 404)
        self.assertEqual(data['error'], 'Not Found')

    def test_unexpected_api_method(self):
        req = {"account": "horns&hoofs",
               "login": "h&f",
               "method": "foo",
               "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
               "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
                             "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}
        self.conn.request("POST", "method", json.dumps(req), self.headers)
        r = self.conn.getresponse()
        data = json.load(r)
        self.assertIn('code', data)
        self.assertIn('error', data)
        self.assertEqual(data['code'], 422)
        self.assertEqual(data['error'], 'Invalid Request')

    def test_clients_interests(self):
        req = {"account": "horns&hoofs",
               "login": "h&f",
               "method": "clients_interests",
               "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
               "arguments": {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}}
        self.conn.request("POST", "/method/", json.dumps(req), self.headers)
        r = self.conn.getresponse()
        data = json.load(r)
        self.assertIn('code', data)
        self.assertIn('response', data)
        response = data['response']
        self.assertEqual(type(response), dict)
        for key, value in response.items():
            self.assertEqual(type(key), str)
            self.assertEqual(type(value), list)


class TestStore(unittest.TestCase):
    store = Store()

    def test_cache_set(self):
        self.assertTrue(self.store.cache_set('key1', 'value1'))

    def test_cache_get(self):
        self.store.cache_set('key2', 'value2')
        value = self.store.cache_get('key2')
        self.assertEqual(value, b'value2')

    def test_cache_timeout(self):
        self.store.cache_set('key3', 'value3', cache_time=2)
        sleep(2)
        value = self.store.cache_get('key3')
        self.assertEqual(value, None)

    def test_set(self):
        self.assertTrue(self.store.set('key4', 'value4'))

    def test_get(self):
        self.store.set('key5', 'value5')
        value = self.store.get('key5')
        self.assertEqual(value, b'value5')


if __name__ == "__main__":
    unittest.main()
