"""
This module contains fixtures for setting up and managing the Django test environment,
configuring database access, and providing reusable setups for authenticated users
and mock RabbitMQ publishers.

Fixtures:
---------
- django_db_setup: Configures the default database settings for in-memory SQLite usage.
- setup_persistent_db: Creates and destroys a persistent test database for use across tests.
- use_persistent_db: Enables test functions to access the persistent database setup.
- shared_data: Provides dictionary-based SharedData class for sharing data across tests within the session scope.
- authorized_user_client: Sets up an authenticated async client instance for testing with an authorized user.
- mock_rmq_publisher: Provides a mock instance of the RabbitMQ publisher, useful for testing without actual RabbitMQ connections.
"""

from http.cookies import SimpleCookie

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connections

from testing_tools.async_client import AsyncClientBoB


def generate_email(name: str) -> str:
    """
    Generates email with domain for tests.
    """

    return f"{name}@test.businessorientedprogramming.com"


class SharedData(dict):
    """
    Data structure build on top of a dict object that allows to assert values under key exist.
    """

    def get(self, key: str):
        """
        Overrides get and assert key exists within SharedData
        """

        assert key in self, f"Key: {key} is not in shared_data"
        return self[key]


class AnonymousUserFactory:
    """
    Class responsible for creation and distribution of AnonymousUsers.
    """

    def __init__(self):
        self._users = {}

    def get_user(self, name: str) -> AsyncClientBoB:
        """
        Gets user by name. If a user is not in a factory, it creates a new one.
        """

        if name not in self._users:
            self._users[name] = self._create(name)

        return self._users[name]

    def _create(self, name: str):
        """
        Creates new anonymous user with cookies as name.
        """

        client = AsyncClientBoB({})
        client.cookies = {"ANONYMOUS_USER_EXTERNAL_ID": name}
        client.uid = name
        return client


class AuthorizedUserFactory(AnonymousUserFactory):
    """
    Factory of authorized users. It creates users and distributes them based on a given name.
    """

    def _create(self, name: str) -> AsyncClientBoB:
        """
        Creates new User and authenticate it.
        """
        email = generate_email(name)
        UserModel = get_user_model()
        user, _ = UserModel.objects.get_or_create(username="test", email=email)
        user_id = user.id
        password = "Password123#@!"
        user.set_password(password)
        user.save()

        # Authorize your user here - the best with use of your inner service.
        assert False

        client = AsyncClientBoB(headers={"Authorization": f"Bearer {access_token}"}, email=email, uid=user_id,
                                password=password, organization_id=organization.id)
        client.cookies = SimpleCookie({settings.REFRESH_TOKEN_KEY: refresh_token})
        client.organization_name = name
        return client


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Configures the default Django database settings to use an in-memory SQLite database
    for efficient testing. Overrides the default database configuration with specific
    options for connection handling and timezone.

    This fixture runs once per test session.
    """
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
        "TIME_ZONE": "America/Chicago",
        "CONN_HEALTH_CHECKS": True,
        "CONN_MAX_AGE": 0,
        "OPTIONS": {},
        "AUTOCOMMIT": True
    }


@pytest.fixture(scope="session")
def setup_persistent_db(django_db_setup, django_db_blocker):
    """
    Sets up a persistent test database using the SQLite in-memory database for the session.
    This fixture creates a test database and keeps it across tests, allowing test functions
    to share data within a single session.

    After the session, the database is destroyed.

    :param django_db_setup: Sets up the initial database configuration.
    :param django_db_blocker: Provides access to manage the database creation and teardown.
    """
    with django_db_blocker.unblock():
        connections["default"].creation.create_test_db(keepdb=True)
    yield
    with django_db_blocker.unblock():
        connections["default"].creation.destroy_test_db(":memory:")


@pytest.fixture(scope="function")
def use_persistent_db(setup_persistent_db, django_db_blocker):
    """
    Provides access to the persistent database within individual test functions.
    This fixture ensures that each test function can connect to the database set up
    by `setup_persistent_db`.

    :param setup_persistent_db: Ensures the database is set up for the session.
    :param django_db_blocker: Allows test functions to unblock database access.
    """
    with django_db_blocker.unblock():
        yield


@pytest.fixture(scope="session")
def shared_data():
    """
    Provides a SharedData to store data that can be shared across tests within the
    same session scope. Useful for sharing setup information like IDs or tokens
    without repeating database calls.

    Yields:
        SharedData: An empty dictionary base class to be populated with shared data as needed.
    """
    data = SharedData()
    yield data


@pytest.fixture(scope="session")
def anonymous_user_factory() -> AnonymousUserFactory:
    """
    Instantiate AnonymousUserFactory and supply it during session.
    """
    factory = AnonymousUserFactory()
    yield factory


@pytest.fixture
def anonymous_user_one(anonymous_user_factory) -> AsyncClientBoB:
    return anonymous_user_factory.get_user("one")


@pytest.fixture
def anonymous_user_for_testing_store(anonymous_user_factory) -> AsyncClientBoB:
    return anonymous_user_factory.get_user("store_test")


@pytest.fixture
def anonymous_user_for_testing_subscription(anonymous_user_factory) -> AsyncClientBoB:
    return anonymous_user_factory.get_user("subscription_test")


@pytest.fixture(scope="session")
def authorized_user_factory() -> AnonymousUserFactory:
    factory = AuthorizedUserFactory()
    yield factory


@pytest.fixture
def authorized_user_one(authorized_user_factory) -> AsyncClientBoB:
    return authorized_user_factory.get_user("one")