# -*- coding: utf-8 -*-
from datetime import datetime
import logging

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Field:
    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable
        self.value = None

    def __get__(self, obj, objtype=None):
        logging.debug(f'get value {self.value}')
        return self.value

    def __set__(self, obj, value):
        if value is None and (self.required or not self.nullable):
            raise AttributeError('Value is required', value)
        elif value is None and self.nullable:
            self.value = value
        else:
            self.validate(value)
            self.value = value

    def validate(self, value):
        raise NotImplementedError


class CharField(Field):

    def validate(self, value):
        logging.debug('validating chars')
        if not (type(value) == str):
            raise ValueError('Char Field got non-string type')


class ListField(Field):

    def validate(self, value):
        logging.debug('validating list')
        if not (type(value) == list):
            raise ValueError('List Field got non-list type')


class DictField(Field):

    def validate(self, value):
        logging.debug('validating list')
        if not (type(value) == dict):
            raise ValueError('Dict Field got non-dict type')


class EmailField(CharField):

    def validate(self, value):
        logging.debug('validating mail')
        super().validate(value)
        if not ('@' in value):
            raise ValueError("No '@' in Email Field")


class PhoneField(Field):

    def validate(self, value):
        logging.debug('validating phone')
        value = str(value)
        if not (len(value) == 11):
            raise ValueError('Phone Field must contain 11 numbers')
        elif not value.isdigit():
            raise ValueError('Phone Field must contain only digits')
        elif not value.startswith('7'):
            raise ValueError("Phone Field must starts with '7'")


class DateField(CharField):

    def validate(self, value):
        logging.debug('validating date')
        super().validate(value)
        date = datetime.strptime(value, "%d.%m.%Y").date()


class BirthDayField(DateField):

    def validate(self, value):
        logging.debug('validating bthday')
        super().validate(value)
        value = datetime.strptime(value, "%d.%m.%Y").date()
        today = datetime.now().date()
        if not (today - value).days // 365 < 70:
            raise ValueError('Incorrect date: (> 70 years old)')


class GenderField(Field):

    def validate(self, value):
        logging.debug('validating gender')
        if value not in (UNKNOWN, MALE, FEMALE):
            raise ValueError('Unexpected gender')


class ClientIDsField(ListField):

    def validate(self, value):
        logging.debug('validating client ids')
        super().validate(value)
        if not all(map(lambda x: type(x) is int, value)):
            raise ValueError('Cliend IDs may contains only integers')


class ArgumentsField(DictField):

    def validate(self, value):
        super().validate(value)
