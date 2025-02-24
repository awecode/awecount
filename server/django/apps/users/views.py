from django.contrib.auth import get_user_model

from rest_framework import status, views
from rest_framework.response import Response

from apps.users.models import Profile

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from apps.users.serializers import UserSerializer


class UserViewset(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    model = get_user_model()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.model.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=["patch"])
    def deactivate(self, request):
        self.get_object().is_active = False
        self.get_object().save()
        return Response({"message": "User deactivated successfully"}, status=status.HTTP_200_OK)


class UpdateUserOnBoardedEndpoint(views.APIView):
    def patch(self, request):
        profile = Profile.objects.get(user_id=request.user.id)
        profile.is_onboarded = request.data.get("is_onboarded", False)
        profile.save()
        return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)
