from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from authentication.models import User
import jwt


def token_required(f):
    """
    required authentication to access
    """
    @wraps(f)
    def decorator(request, *args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers.get('Authorization')

        if token is None:
            return Response({
                "error": "token required!"
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = jwt.decode(
                token.split()[1],
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

        except Exception:
            return Response({
                "error": "Invalid token!"
            }, status=status.HTTP_400_BAD_REQUEST)

        current_user = User.objects.filter(id=data['id']).first()

        if current_user is None:
            return Response({
                "error": "incorrect username or password!"
            }, status=status.HTTP_400_BAD_REQUEST)

        request.session['user_id'] = current_user.id

        request.session["user_id"] = current_user.id
        return f(request, current_user, *args, **kwargs)

    return decorator
