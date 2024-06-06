import argparse
import os
import pathlib
import sys

sys.path.append(os.path.join(pathlib.Path(__file__).parents[1]))

from cd.define import CertificationElements

from chip.tlv import TLVReader

from pyasn1.codec.der.decoder import decode as der_decoder
from pyasn1.error import PyAsn1Error
from pyasn1_modules import rfc5652


def parse_cd(cd_file_data):
    cert_elements = CertificationElements()

    try:
        temp, _ = der_decoder(cd_file_data, asn1Spec=rfc5652.ContentInfo())
    except PyAsn1Error as e:
        print(e)
        return None

    layer1 = dict(temp)
    temp, _ = der_decoder(layer1['content'].asOctets(), asn1Spec=rfc5652.SignedData())

    signed_data = dict(temp)
    encap_content_info = dict(signed_data['encapContentInfo'])
    cd_tlv = bytes(encap_content_info['eContent'])

    cd_content = TLVReader(cd_tlv).get()["Any"]
    cert_elements.format_version = cd_content[0]
    cert_elements.vendor_id = cd_content[1]
    cert_elements.product_id_array = cd_content[2]
    cert_elements.device_type_id = cd_content[3]
    cert_elements.certificate_id = cd_content[4]
    cert_elements.security_level = cd_content[5]
    cert_elements.security_info = cd_content[6]
    cert_elements.version_number = cd_content[7]
    cert_elements.certification_type = cd_content[8]
    if 9 in cd_content.keys():
        cert_elements.origin_vid = cd_content[9]
    if 10 in cd_content.keys():
        cert_elements.origin_pid = cd_content[10]
    if 11 in cd_content.keys():
        cert_elements.paa_authority_list = cd_content[11]

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
    with open(args.cd_file, "rb") as f:
        file_bytes = f.read()
    cd = parse_cd(file_bytes)
    if not cd:
        sys.exit(1)
    else:
        print(cd)
        sys.exit(0)
