from django.test import TestCase


class MyTest(TestCase):
    def setUp(self):
        self.a = 1

    def testA(self):
        self.assertEqual(self.a, 1)