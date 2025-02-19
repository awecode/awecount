from rest_framework import status, views
from rest_framework.response import Response

from apps.users.models import Profile


class UpdateUserOnBoardedEndpoint(views.APIView):
    def patch(self, request):
        profile = Profile.objects.get(user_id=request.user.id)
        profile.is_onboarded = request.data.get("is_onboarded", False)
        profile.save()
        return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)
