# myapp/tests/test_api_myapp.py
import pytest
from rest_framework import status
from django.urls import reverse

# Exemplu: test pentru list (necesită auth și eventual fixture MyModel)
# def test_list_requires_auth(client):
#     url = reverse("mymodel-list")
#     response = client.get(url)
#     assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
