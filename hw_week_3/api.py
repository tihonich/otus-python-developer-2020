# -*- coding: utf-8 -*-
from _datetime import datetime
import hashlib
import functools
from fields import CharField, EmailField, PhoneField, BirthDayField, DateField
from fields import Field, ArgumentsField, ClientIDsField, GenderField
from scoring import get_score, get_interests
import logging


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500

ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}


class ApiRequest:
    def __init__(self, **kwargs):
        self.api_fields = [k for k, v in self.__class__.__dict__.items()
                           if isinstance(v, Field)]
        logging.debug(f'API FIELDS {self.api_fields}')
        bad_fields = []
        required_field_errs = []
        self.has = []
        for field in self.api_fields:
            if field in kwargs:
                value = kwargs[field]
                self.has.append(field)
            else:
                value = None
            try:
                logging.debug(f'SET {field} TO {value}')
                setattr(self, field, value)
            except ValueError as e:
                logging.debug(f'FAILED TO SET {field} TO {value}')
                bad_fields.append((field, e.args[0]))
            except AttributeError:
                required_field_errs.append(field)
        if required_field_errs:
            raise AttributeError(f'This fields is required: {required_field_errs}')
        if bad_fields:
            raise TypeError(f'Bad fields: {bad_fields}')
        logging.debug('CALL REQUEST VALIDATE')
        self.validate()

    def validate(self):
        return True


class ClientsInterestsRequest(ApiRequest):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(ApiRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        validating_pairs = [
            ('first_name', 'last_name'),
            ('email', 'phone'),
            ('birthday', 'gender'),
        ]
        if ('first_name' in self.has and 'last_name' in self.has) or \
            ('email' in self.has and 'phone' in self.has) or \
            ('birthday' in self.has and 'gender' in self.has):
            return True
        else:
            raise AttributeError("Required at least one of this fields pars: ('first_name', 'last_name'), "
                                 "('email', 'phone'), ('birthday', 'gender')")


class MethodRequest(ApiRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request: MethodRequest):
    if request.login == ADMIN_LOGIN:
        digest = hashlib.sha512((datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf-8')).hexdigest()
    logging.info(f'DIGEST: {digest}')
    if digest == request.token:
        return True
    return False


def login_required(method_handler: callable):
    @functools.wraps(method_handler)
    def wrapper(request: MethodRequest, ctx, store):
        if check_auth(request):
            res = method_handler(request, ctx, store)
        else:
            res = (FORBIDDEN, ERRORS[FORBIDDEN])
        return res
    return wrapper


def method_handler(request, ctx, store):
    methods = {
        'online_score': online_score_handler,
        'clients_interests': clients_interests_handler,
    }
    try:
        req_obj = MethodRequest(**request["body"])
        code, response = methods[req_obj.method](req_obj, ctx, store)
    except AttributeError as e:
        return INVALID_REQUEST, e.args[0]
    except TypeError as e:
        return INVALID_REQUEST, e.args[0]
    else:
        return code, response


@login_required
def online_score_handler(request: MethodRequest, ctx, store):
    api_request = OnlineScoreRequest(**request.arguments)
    logging.debug(f'HAS: {api_request.has}')
    ctx['has'] = api_request.has
    score = get_score(store,
                      phone=api_request.phone,
                      email=api_request.email,
                      birthday=api_request.birthday,
                      gender=api_request.gender,
                      first_name=api_request.first_name,
                      last_name=api_request.last_name)
    return OK, {"score": score}


@login_required
def clients_interests_handler(request: MethodRequest, ctx, store):
    api_request = ClientsInterestsRequest(**request.arguments)
    logging.debug(f'HAS: {api_request.has}')
    ctx['has'] = api_request.has
    return OK, {cid: get_interests(store, cid) for cid in api_request.client_ids}
