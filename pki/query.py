import json

import requests

from config.define import baseUrl


def query_root_certificates() -> (bool, str, list):
    try:
        response = requests.get(
            f"{baseUrl}/dcl/pki/root-certificates"
        )
        resp_data = response.json()
        return True, "", resp_data["approvedRootCertificates"]["certs"]
    except Exception as e:
        return False, str(e), None


def query_certificates(subject, subject_key_id) -> (bool, str, object):
    try:
        response = requests.get(
            f"{baseUrl}/dcl/pki/certificates/"
            f"{subject}/{subject_key_id}"
        )
        resp_data = response.json()
        return True, "", resp_data["approvedCertificates"]
    except Exception as e:
        return False, str(e), None
