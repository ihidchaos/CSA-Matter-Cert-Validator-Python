import json

import requests

from config.define import baseUrl


def query_vendor_info(cd) -> (bool, str, object):
    try:
        response = requests.get(
            f"{baseUrl}/dcl/vendorinfo/vendors/"
            f"{cd.vendor_id}"
        )
        if response.status_code == requests.codes.not_found:
            return False, f"厂商ID:{cd.vendor_id}不在DCL上", None
        if response.status_code != requests.codes.ok:
            return False, f"错误码:{response.status_code}", None
        resp_data = response.json()
        return True, "", resp_data["vendorInfo"]
    except Exception as e:
        return False, str(e), None


def query_model_info(cd) -> (bool, str, object):
    try:
        response = requests.get(
            f"{baseUrl}/dcl/model/models/"
            f"{cd.vendor_id}/{cd.product_id_array[-1]}"
        )
        if response.status_code == requests.codes.not_found:
            return False, f"产品ID:{cd.product_id_array[-1]}不在DCL上", None
        if response.status_code != requests.codes.ok:
            return False, f"错误码:{response.status_code}", None
        resp_data = response.json()
        return True, "", resp_data["model"]
    except Exception as e:
        return False, str(e), None


def query_compliance_info(cd) -> (bool, str, object):
    try:
        response = requests.get(
            f"{baseUrl}/dcl/compliance/compliance-info/"
            f"{cd.vendor_id}/{cd.product_id_array[-1]}/{cd.version_number}/matter"
        )
        if response.status_code == requests.codes.not_found:
            return False, f"{cd.vendor_id}/{cd.product_id_array[-1]}/{cd.version_number}合约信息不在DCL上", None
        if response.status_code != requests.codes.ok:
            return False, f"错误码:{response.status_code}", None
        resp_data = response.json()
        return True, "", resp_data["complianceInfo"]
    except Exception as e:
        return False, str(e), None
