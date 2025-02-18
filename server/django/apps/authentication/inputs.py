from allauth.headless.internal.restkit import inputs


class EmailCheckInput(inputs.Input):
    email = inputs.EmailField(required=True)
