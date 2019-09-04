import pytest
import falcon
import json
import unittest
from unittest.mock import Mock, MagicMock, patch
from history import app
from history.api import models
from history.api.models import DeviceHistory
from falcon import testing

class TestDeviceHistory(testing.TestCase):
    @pytest.fixture()
    def client():
        return testing.TestClient(app.app):
