
from drf_yasg import openapi


def __propertisValaidateEmailForm():
    return [
        openapi.Parameter(
            'token', openapi.IN_PATH, description="from request", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter(
            'userID', openapi.IN_PATH, description="pk", type=openapi.TYPE_INTEGER)
    ]


def validateEmailDocs():

    response = openapi.Response(
        description='response is correct',
        type=openapi.TYPE_OBJECT,
        schema=openapi.Schema(
            title="",
            type=openapi.TYPE_OBJECT,
            properties={
                    'user': openapi.Schema(type=openapi.TYPE_STRING, description="message"),
            }
        )
    )

    return response, __propertisValaidateEmailForm()


# Change password
def userSwagger(title, description, name):
    fieldRequired = ['password', 'newPassword']

    response_post = openapi.Response(
        title=title,
        description=description,
        type=openapi.TYPE_OBJECT,
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'result': openapi.Schema(type=openapi.TYPE_STRING, description="message"),
            }
        )
    )

    request_body_post = openapi.Schema(
        title=title,
        type=openapi.TYPE_OBJECT,
        required=fieldRequired,
        properties={
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="password of {}".format(name)),
            'newPassword': openapi.Schema(type=openapi.TYPE_STRING, description="new password of {}".format(name)),
        }
    )

    return response_post, request_body_post


# Reset password
def resetPasswordSwagger(title, description, name):
    fieldRequired = ['email']

    response_post = openapi.Response(
        title=title,
        description=description,
        type=openapi.TYPE_OBJECT,
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'result': openapi.Schema(type=openapi.TYPE_STRING, description="message"),
            }
        )
    )

    request_body_post = openapi.Schema(
        title=title,
        type=openapi.TYPE_OBJECT,
        required=fieldRequired,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="email from account"),
        }
    )

    return response_post, request_body_post


# Update Reset password
def updateResetPasswordSwagger(title, description, name):
    fieldRequired = ['email']

    pathParams = [
        openapi.Parameter(
            'token', openapi.IN_PATH, description="from request", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter(
            'userID', openapi.IN_PATH, description="pk", type=openapi.TYPE_INTEGER)
    ]

    response_post = openapi.Response(
        title=title,
        description=description,
        type=openapi.TYPE_OBJECT,
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'result': openapi.Schema(type=openapi.TYPE_STRING, description="message"),
            }
        )
    )

    request_body_post = openapi.Schema(
        title=title,
        type=openapi.TYPE_OBJECT,
        required=fieldRequired,
        properties={
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="password from user"),
        }
    )

    return response_post, request_body_post, pathParams
