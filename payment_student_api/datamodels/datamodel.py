# -*- coding: utf-8 -*-
from marshmallow import fields
from odoo.addons.datamodel.core import Datamodel
#from odoo.addons.datamodel.fields import NestedModel

class Response(Datamodel):
    class Meta:
        ordered = True

    _name = "response"

    response_code = fields.Integer(required=True, allow_none=False, title="Response Code", description="Integer which is returned to represent response", example=0)
    response_message = fields.String(required=True, allow_none=False, title="Response Message", description="Description which is returned to represent response", example="Success")

class ApiKeys(Datamodel):
    class Meta:
        ordered = True

    _name = "api.keys"

    application_key = fields.String(required=True, allow_none=False, title="Application Key", description="API Key which is acquired by your service provider", example="1x2cdaa3-35df-2eff-aeq2-5d74387701xd")

class ApiSecretKeys(Datamodel):
    class Meta:
        ordered = True

    _name = "api.secret.keys"
    _inherit = "api.keys"

    secret_key = fields.String(required=True, allow_none=False, title="Secret Key", description="Secret Key which is given to you by your service provider", example="xa18a2325z80c73ay871au54ba169c76")

class SchoolSearch(Datamodel):
    class Meta:
        ordered = True

    _name = "school.search"
    _inherit = "api.keys"

    page = fields.Integer(required=True, allow_none=False, title="Page Number", description="Records are paged hundred by hundred. Given page number will be used when getting desired records. First page starts with 1.", example="1")
    code = fields.String(required=False, allow_none=False, title="School Code", description="A part of school code can be entered. For example, when you enter 'JOH', the codes which contain this word will be listed. It is not a required field.", example="JOHNDC")
    name = fields.String(required=False, allow_none=False, title="School Name", description="A part of school name can be entered. For example, when you enter 'College', the names which contain this word will be listed. It is not a required field.", example="John Doe College")

class ClassSearch(Datamodel):
    class Meta:
        ordered = True

    _name = "class.search"
    _inherit = "api.keys"

    page = fields.Integer(required=True, allow_none=False, title="Page Number", description="Records are paged hundred by hundred. Given page number will be used when getting desired records. First page starts with 1.", example="1")
    code = fields.String(required=False, allow_none=False, title="Class Code", description="A part of class code can be entered. For example, when you enter 'CLA', the codes which contain this word will be listed. It is not a required field.", example="CLASS1")
    name = fields.String(required=False, allow_none=False, title="Class Name", description="A part of class name can be entered. For example, when you enter 'Clas', the names which contain this word will be listed. It is not a required field.", example="Class 1")

class BursarySearch(Datamodel):
    class Meta:
        ordered = True

    _name = "bursary.search"
    _inherit = "api.keys"

    page = fields.Integer(required=True, allow_none=False, title="Page Number", description="Records are paged hundred by hundred. Given page number will be used when getting desired records. First page starts with 1.", example="1")
    code = fields.String(required=False, allow_none=False, title="Bursary Code", description="A part of bursary code can be entered. For example, when you enter 'BUR', the codes which contain this word will be listed. It is not a required field.", example="BURSARY50")
    name = fields.String(required=False, allow_none=False, title="Bursary Name", description="A part of bursary name can be entered. For example, when you enter 'Clas', the names which contain this word will be listed. It is not a required field.", example="Bursary 50%")

class StudentSearch(Datamodel):
    class Meta:
        ordered = True

    _name = "student.search"
    _inherit = "api.keys"

    page = fields.Integer(required=True, allow_none=False, title="Page Number", description="Records are paged hundred by hundred. Given page number will be used when getting desired records. First page starts with 1.", example="1")
    name = fields.String(required=False, allow_none=False, title="Student Name", description="Student name", example="Jane Doe")
    vat = fields.String(required=False, allow_none=False, title="Student ID Number", description="Student citizen number", example="12345678912")

class PaymentSearch(Datamodel):
    class Meta:
        ordered = True

    _name = "payment.search"
    _inherit = "api.keys"

    page = fields.Integer(required=True, allow_none=False, title="Page Number", description="Records are paged hundred by hundred. Given page number will be used when getting desired records. First page starts with 1.", example="1")
    email = fields.String(required=True, allow_none=False, title="Email", description="Email address", example="test@example.com")

class SchoolResponse(Datamodel):
    class Meta:
        ordered = True

    _name = "school.response"
    _inherit = "response"

    schools = fields.List(fields.Dict, title="Schools", description="List of schools", example=[{"id": 26, "name": "John Doe College", "code": "JOHNDC"}])

class ClassResponse(Datamodel):
    class Meta:
        ordered = True

    _name = "class.response"
    _inherit = "response"

    classes = fields.List(fields.Dict, title="Classes", description="List of classes", example=[{"id": 34, "name": "Class 1", "code": "CLASS1"}])

class BursaryResponse(Datamodel):
    class Meta:
        ordered = True

    _name = "bursary.response"
    _inherit = "response"

    bursaries = fields.List(fields.Dict, title="Bursaries", description="List of bursaries", example=[{"id": 12, "name": "Bursary 50%", "code": "BURSARY50"}])

class StudentResponse(Datamodel):
    class Meta:
        ordered = True

    _name = "student.response"
    _inherit = "response"

    students = fields.List(fields.Dict, title="Students", description="List of students", example=[{"id": 52, "name": "Jane Doe", "vat": "12345678912", "parent": "John Doe"}])

class PaymentResponse(Datamodel):
    class Meta:
        ordered = True

    _name = "payment.response"
    _inherit = "response"

    payments = fields.List(fields.Dict, title="Payments", description="List of payments", example=[{"id": 76, "date": "25-01-2021", "amount": 145.30, "state": "done"}])


class StudentCreate(Datamodel):
    class Meta:
        ordered = True

    _name = "student.create"
    _inherit = "api.secret.keys"

    name = fields.String(required=True, allow_none=False, title="Student Name", description="Student name", example="Jane Doe")
    vat = fields.String(required=True, allow_none=False, title="Student ID Number", description="Student citizen number", example="12345678912")
    school_code = fields.String(required=True, allow_none=False, title="School Code", description="School codename", example="JOHNDC")
    bursary_code = fields.String(allow_none=True, title="Bursary Code", description="Bursary codename", example="BURSARY50")
    class_code = fields.String(required=True, allow_none=False, title="Class Code", description="Class codename", example="CLASS1")
    parent_name = fields.String(required=True, allow_none=False, title="Parent Name", description="Parent name of related student", example="John Doe")
    parent_email = fields.String(required=True, allow_none=False, title="Parent Email", description="Email address of related parent", example="test@example.com")
    parent_mobile = fields.String(required=True, allow_none=False, title="Parent Mobile", description="Mobile phone number of related parent", example="+905001234567")
    ref = fields.String(required=True, allow_none=False, title="Ref", description="Student your REF number", example="ABC01")


class StudentDelete(Datamodel):
    class Meta:
        ordered = True

    _name = "student.delete"
    _inherit = "api.secret.keys"

    vat = fields.String(required=True, allow_none=False, title="Student ID Number", description="Student citizen number", example="12345678912")
