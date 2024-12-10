import os
import uuid

from django.conf import settings
from django.core.signing import BadSignature, Signer
from django.utils.crypto import constant_time_compare


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
    filename = f"{uuid.uuid4()}-{file.name}"
    if folder:
        filename = f"{folder}/{filename}"
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, folder)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, folder))
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    with open(file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return filename
