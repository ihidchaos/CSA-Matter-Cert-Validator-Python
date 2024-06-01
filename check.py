#!/usr/bin/env python3

import argparse
import json
import re
import sys

import requests

from cd.parser import parse_cd

baseUrl = "https://on.dcl.csa-iot.org"

hoorii_console_field_max_len = 32

report_data = {}


def add_report_data(name, data, reason):
    report_data[name] = {"数值": data, "问题": reason}


def has_abnormal_spaces(string, name):
    # 检查尾部是否含有空格
    has_trailing_spaces = string != string.rstrip()

    # 使用正则表达式检查是否包含两个及以上的连续空格
    has_double_or_more_spaces = re.search(r'\s{2,}', string) is not None

    # 返回两者的逻辑或结果
    if has_trailing_spaces or has_double_or_more_spaces:
        reason = f"有额外空格"
        add_report_data(name, string, reason)
        return True
    return False


def len_exceeded(string, name):
    if len(string) > hoorii_console_field_max_len:
        reason = f"长度超出{hoorii_console_field_max_len}"
        add_report_data(name, string, reason)
        return True
    return False


def check_vendor_info_valid(vendor_info_data: dict):
    vendor_name = vendor_info_data["vendorName"]
    vendor_name_invalid = has_abnormal_spaces(vendor_name, "vendorName") or len_exceeded(vendor_name, "vendorName")
    return not vendor_name_invalid


def check_models_valid(models_data: dict):
    product_name = models_data["productName"]
    product_label = models_data["productLabel"]

    product_name_invalid = (has_abnormal_spaces(product_name, "productName") or
                            len_exceeded(product_name, "productName"))

    product_label_invalid = (has_abnormal_spaces(product_label, "productLabel") or
                             len_exceeded(product_label, "productLabel"))
    return not (product_name_invalid or product_label_invalid)


def check_compliance_info_valid(compliance_info_data: dict, certificate_id):
    cd_certificate_id = compliance_info_data["cDCertificateId"]
    if cd_certificate_id != certificate_id:
        reason = f"CD内ID{certificate_id}与DCL信息{cd_certificate_id}不匹配"
        add_report_data(certificate_id, "certificateID", reason)
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse CD File And Check Validity")
    parser.add_argument(
        "cd_file",
        type=str,
        help="CD File",
    )
    args = parser.parse_args()
    cd = parse_cd(args.cd_file)
    if not cd:
        sys.exit(1)
    print(cd)

    try:
        response = requests.get(
            f"{baseUrl}/dcl/vendorinfo/vendors/"
            f"{cd.vendor_id}"
        )
        if response.status_code == requests.codes.not_found:
            print(f"厂商ID:{cd.vendor_id}不在DCL上")
            sys.exit(1)
        if response.status_code != requests.codes.ok:
            print(response.status_code)
            sys.exit(1)
        resp_data = response.json()
        print(json.dumps(resp_data, indent=4))
        check_vendor_info_valid(resp_data["vendorInfo"])
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        response = requests.get(
            f"{baseUrl}/dcl/model/models/"
            f"{cd.vendor_id}/{cd.product_id_array[-1]}"
        )
        resp_data = response.json()
        print(json.dumps(resp_data, indent=4))
        check_models_valid(resp_data["model"])
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        response = requests.get(
            f"{baseUrl}/dcl/compliance/compliance-info/"
            f"{cd.vendor_id}/{cd.product_id_array[-1]}/{cd.version_number}/matter"
        )
        resp_data = response.json()
        print(json.dumps(resp_data, indent=4))
        check_compliance_info_valid(
            resp_data["complianceInfo"], cd.certificate_id
        )
    except Exception as e:
        print(e)
        sys.exit(1)

    if report_data:
        print("检测到以下问题:")
        print(json.dumps(report_data, indent=4, ensure_ascii=False))
        sys.exit(1)
    else:
        print("没有检测到问题")
        sys.exit(0)
