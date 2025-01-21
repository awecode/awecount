from .company_join import process_company_invitations


def post_user_auth_workflow(user, is_signup, request):
    process_company_invitations(user=user)
