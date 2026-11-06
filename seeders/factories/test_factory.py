from faker import Faker
from app.models.test_model import TestModel

fake = Faker("es_ES")


def make_test() -> TestModel:
    return TestModel(
        # test_name es unique
        test_name=fake.unique.word() + str(fake.unique.random_number(digits=5)),
        test_type=fake.random_element(["unit", "integration", "e2e"]),
    )
