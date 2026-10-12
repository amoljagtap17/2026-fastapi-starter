import pytest

class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def default_employee():
    return Student('John', 'Doe', 'Computer Science', 3)

"""
Pytest Fixtures:

default_employee: Provides a default Student instance with first name 'John', last name 'Doe', major 'Computer Science', and 3 years of study.

"""

def test_person_initialization(default_employee):
    assert default_employee.first_name == 'John', 'First name should be John'
    assert default_employee.last_name == 'Doe', 'Last name should be Doe'
    assert default_employee.major == 'Computer Science'
    assert default_employee.years == 3