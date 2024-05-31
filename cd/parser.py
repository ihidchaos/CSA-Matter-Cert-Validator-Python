import argparse
import os
import pathlib
import sys
sys.path.append(os.path.join(pathlib.Path(__file__).parents[1]))

from chip.tlv import TLVReader

from pyasn1.codec.der.decoder import decode as der_decoder
from pyasn1.error import PyAsn1Error
from pyasn1_modules import rfc5652


"""
参考自：
1. https://github.com/project-chip/connectedhomeip/blob/master/src/python_testing/TC_DA_1_2.py
2. https://github.com/project-chip/connectedhomeip/tree/master/src/controller/python/chip/tlv
"""


class CertificationElements:
    def __init__(self):
        self.format_version = 0
        self.vendor_id = 0
        self.product_id_array = []
        self.product_ids_count = 0
        self.device_type_id = 0
        self.certificate_id = ""
        self.security_level = 0
        self.security_info = 0
        self.version_number = 0
        self.certification_type = 0
        self.origin_vid = 0
        self.origin_pid = 0
        self.paa_authority_list = []
        self.paa_authority_count = 0

    def __str__(self):
        product_ids_str = ", ".join(map(str, self.product_id_array))
        authorized_paa_list_str = ", ".join(
            str(paa.hex()).upper() for paa in self.paa_authority_list) if self.paa_authority_count > 0 else ""

        output = (
            f"Certification Elements:\n"
            f"  Format Version: {self.format_version}\n"
            f"  Vendor ID: {self.vendor_id}\n"
            f"  Product IDs: {product_ids_str}\n"
            f"  Product IDs Count: {self.product_ids_count}\n"
            f"  Device Type ID: {self.device_type_id}\n"
            f"  Certificate ID: {self.certificate_id}\n"
            f"  Security Level: {self.security_level}\n"
            f"  Security Information: {self.security_info}\n"
            f"  Version Number: {self.version_number}\n"
            f"  Certification Type: {self.certification_type}\n"
        )

        # 判断origin_vid和origin_pid是否为0，不为0时才添加进输出
        if self.origin_vid != 0 or self.origin_pid != 0:
            output += (
                f"  DAC Origin Vendor ID: {self.origin_vid}\n"
                f"  DAC Origin Product ID: {self.origin_pid}\n"
            )

            # 判断paa_authority_count是否为0，不为0时才添加进输出
        if self.paa_authority_count > 0:
            output += (
                f"  Authorized PAA List: {authorized_paa_list_str}\n"
                f"  Authorized PAA List Count: {self.paa_authority_count}\n"
            )

        return output


def parse_cd(cd_file):
    cert_elements = CertificationElements()

    with open(cd_file, "rb") as f:
        cd_file_data = f.read()

    try:
        temp, _ = der_decoder(cd_file_data, asn1Spec=rfc5652.ContentInfo())
    except PyAsn1Error:
        sys.exit("Unable to decode CD - improperly encoded DER")

    layer1 = dict(temp)
    temp, _ = der_decoder(layer1['content'].asOctets(), asn1Spec=rfc5652.SignedData())

    signed_data = dict(temp)
    encap_content_info = dict(signed_data['encapContentInfo'])
    cd_tlv = bytes(encap_content_info['eContent'])

    cd = TLVReader(cd_tlv).get()["Any"]
    cert_elements.format_version = cd[0]
    cert_elements.vendor_id = cd[1]
    cert_elements.product_id_array = cd[2]
    cert_elements.device_type_id = cd[3]
    cert_elements.certificate_id = cd[4]
    cert_elements.security_level = cd[5]
    cert_elements.security_info = cd[6]
    cert_elements.version_number = cd[7]
    cert_elements.certification_type = cd[8]
    if 9 in cd.keys():
        cert_elements.origin_vid = cd[9]
    if 10 in cd.keys():
        cert_elements.origin_pid = cd[10]
    if 11 in cd.keys():
        cert_elements.paa_authority_list = cd[11]

    cert_elements.product_ids_count = len(cert_elements.product_id_array)
    cert_elements.paa_authority_count = len(cert_elements.paa_authority_list)
    return cert_elements


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print CD File")
    parser.add_argument(
        "cd_file",
        type=str,
        help="CD File",
    )
    args = parser.parse_args()
    cd = parse_cd(args.cd_file)
    if not cd:
        sys.exit(1)
    else:
        print(cd)
        sys.exit(0)
