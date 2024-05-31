#!/usr/bin/env python3

import argparse
import json
import sys

import requests

from cd.parser import parse_cd

baseUrl = "https://on.dcl.csa-iot.org"

hoorii_console_field_max_len = 32


def has_trailing_spaces(s):
    return s != s.rstrip()


def len_exceeded(s):
    return len(s) > hoorii_console_field_max_len


def check_vendor_info_valid(vendor_info_data: dict):
    vendor_name = vendor_info_data["vendorName"]

    if has_trailing_spaces(vendor_name):
        print(f"vendorName:{vendor_name}尾部有多余空格")

    if len_exceeded(vendor_name):
        print(f"vendorName:{vendor_name}长度超出{hoorii_console_field_max_len}")


def check_models_valid(models_data: dict):
    product_name = models_data["productName"]
    product_label = models_data["productLabel"]

    if has_trailing_spaces(product_name):
        print(f"productName:{product_name}尾部有多余空格")

    if len_exceeded(product_name):
        print(f"productName:{product_name}长度超出{hoorii_console_field_max_len}")

    if has_trailing_spaces(product_label):
        print(f"productLabel:{product_label}尾部有多余空格")

    if len_exceeded(product_label):
        print(f"productLabel:{product_label}长度超出{hoorii_console_field_max_len}")


def check_compliance_info_valid(compliance_info_data: dict, certificate_id):
    cd_certificate_id = compliance_info_data["cDCertificateId"]
    if cd_certificate_id != certificate_id:
        print("CD ID不匹配")


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
        data = response.json()
        print(json.dumps(data, indent=4))
        check_vendor_info_valid(data["vendorInfo"])
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        response = requests.get(
            f"{baseUrl}/dcl/model/models/"
            f"{cd.vendor_id}/{cd.product_id_array[-1]}"
        )
        data = response.json()
        print(json.dumps(data, indent=4))
        check_models_valid(data["model"])
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        response = requests.get(
            f"{baseUrl}/dcl/compliance/compliance-info/"
            f"{cd.vendor_id}/{cd.product_id_array[-1]}/{cd.version_number}/matter"
        )
        data = response.json()
        print(json.dumps(data, indent=4))
        check_compliance_info_valid(
            data["complianceInfo"], cd.certificate_id
        )
    except Exception as e:
        print(e)
        sys.exit(1)

    sys.exit(0)
