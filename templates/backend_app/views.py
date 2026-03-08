# myapp/views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MyModel
from .serializers import MyModelSerializer


class MyModelListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = MyModel.objects.all()
        serializer = MyModelSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MyModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
