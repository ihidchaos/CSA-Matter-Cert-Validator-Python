#!/usr/bin/env python3

import argparse
import json
import os
import pathlib
import pprint
import re
import sys

sys.path.append(os.path.join(pathlib.Path(__file__).parents[1]))

from cd import query as cd_query
from pki import query as pki_query
from cd.parser import parse_cd
from config.define import field_max_len
from utils.string import add_colon_every_two_chars
from cd.define import CertificationElements

report_data = {}


def add_report_data(name, data, problem):
    global report_data
    report_data[name] = {"数值": data, "问题": problem}


def has_abnormal_spaces(string, name):
    # 检查尾部是否含有空格
    has_trailing_spaces = string != string.rstrip()

    # 使用正则表达式检查是否包含两个及以上的连续空格
    has_double_or_more_spaces = re.search(r'\s{2,}', string) is not None

    # 返回两者的逻辑或结果
    if has_trailing_spaces or has_double_or_more_spaces:
        problem = f"有额外空格"
        add_report_data(name, string, problem)
        return True
    return False


def len_exceeded(string, name):
    if len(string) > field_max_len:
        problem = f"长度超出{field_max_len}"
        add_report_data(name, string, problem)
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
        problem = f"CD内ID{certificate_id}与DCL信息{cd_certificate_id}不匹配"
        add_report_data(certificate_id, "certificateID", problem)
        return False
    return True


def map_paa_with_name(cd: CertificationElements):
    ok, msg, root_certificates = pki_query.query_root_certificates()
    for paa in cd.paa_authority_list:
        paa_str = paa.hex().upper()
        subject_key_id = add_colon_every_two_chars(paa_str)
        for cert in root_certificates:
            if cert["subjectKeyId"] == subject_key_id:
                subject = cert["subject"]
                ok, msg, certificate = pki_query.query_certificates(subject, subject_key_id)
                certs = certificate["certs"]
                for cert in certs:
                    if cert["subjectKeyId"] == subject_key_id:
                        subject_text = cert["subjectAsText"]
                        cd.append_paa_authority_list_name(subject_text)


def validate_cd(cd):
    global report_data
    report_data = {}
    return_data = {}
    fail_msg = []

    # return_data["cd_file_content"] = cd
    ok, msg, vendor_info = cd_query.query_vendor_info(cd)
    if not ok:
        fail_msg.append(msg)
    else:
        return_data["dcl_vendor_info"] = vendor_info
        check_vendor_info_valid(vendor_info)

    ok, msg, model_info = cd_query.query_model_info(cd)
    if not ok:
        fail_msg.append(msg)
    else:
        return_data["dcl_model_info"] = model_info
        check_models_valid(model_info)

    ok, msg, compliance_info = cd_query.query_compliance_info(cd)
    if not ok:
        fail_msg.append(msg)
    else:
        return_data["dcl_compliance_info"] = compliance_info
        check_compliance_info_valid(compliance_info, cd.certificate_id)

    return_data["validator"] = {
        "is_valid": False if report_data else True,
        "dcl_problem": fail_msg if fail_msg else None,
        "cd_problem": report_data if report_data else None,
    }
    return return_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse CD File And Check Validity")
    parser.add_argument(
        "cd_file",
        type=str,
        help="CD File",
    )
    args = parser.parse_args()
    with open(args.cd_file, "rb") as f:
        file_bytes = f.read()
    cd_data = parse_cd(file_bytes)
    if not cd_data:
        sys.exit(1)
    map_paa_with_name(cd_data)
    print(cd_data.to_ascii_table())
    return_data = validate_cd(cd_data)
    print(json.dumps(return_data, indent=4, ensure_ascii=False))
    sys.exit(0)
