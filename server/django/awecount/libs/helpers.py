import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.signing import BadSignature, Signer
from django.utils.crypto import constant_time_compare
from requests import Request


def merge_dicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(merge_dicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def choice_parser(options, add_blank=False):
    data = [{"value": option[0], "text": option[1]} for option in options]
    if add_blank:
        data.insert(0, {"value": "", "text": "--------"})
    return data


def get_verification_hash(value: str):
    signer = Signer(salt="awecount.verification.hash")
    return signer.sign(value)


def check_verification_hash(hash_to_check, value):
    """
    Checks the received verification hash against this order number.
    Returns False if the verification failed, True otherwise.
    """
    signer = Signer(salt="awecount.verification.hash")
    try:
        signed_number = signer.unsign(hash_to_check)
    except BadSignature:
        return False

    return constant_time_compare(signed_number, value)


def upload_file(file, folder):
    filename = f"{uuid.uuid4()}{file.name[file.name.rfind('.'):]}"
    if folder:
        filename = f"{folder}/{filename}"
    file_path = default_storage.save(filename, ContentFile(file.read()))
    return file_path


def get_origin():
    return settings.URL


def serialize_request(request):
    """Convert a Request object into a dictionary."""
    return {
        "company_id": request.company.id,
        "user": request.user,
        "data": request.data,
        "company": request.company,
    }


def deserialize_request(request_obj):
    """Convert a dictionary into a Request object."""
    request = Request()
    for key, value in request_obj.items():
        setattr(request, key, value)
    return request


def use_miti(company):
    return company.config_template == "np"


def get_full_file_url(request, relative_path):
    return request.build_absolute_uri(default_storage.url(relative_path))


def get_relative_file_path(file_url):
    parts = file_url.split(settings.MEDIA_URL)
    if len(parts) > 1:
        return parts[1]
    return file_url
