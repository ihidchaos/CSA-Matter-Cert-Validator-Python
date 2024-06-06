import json
import os
import pathlib
import sys

sys.path.append(os.path.join(pathlib.Path(__file__).parents[1]))

from prettytable import PrettyTable

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

        self._paa_authority_list_name = []

    def __str__(self):
        product_ids_str = ", ".join(f"{pid} (0x{pid:X})" for pid in self.product_id_array)
        authorized_paa_list_str = ", ".join(
            str(paa.hex()).upper() for paa in self.paa_authority_list) if self.paa_authority_count > 0 else ""

        output = (
            f"Certification Elements:\n"
            f"  Format Version: {self.format_version}\n"
            f"  Vendor ID: {self.vendor_id} (0x{self.vendor_id:X})\n"
            f"  Product IDs: {product_ids_str}\n"
            f"  Product IDs Count: {self.product_ids_count}\n"
            f"  Device Type ID: {self.device_type_id} (0x{self.device_type_id:X})\n"
            f"  Certificate ID: {self.certificate_id}\n"
            f"  Security Level: {self.security_level}\n"
            f"  Security Information: {self.security_info}\n"
            f"  Version Number: {self.version_number}\n"
            f"  Certification Type: {self.certification_type}\n"
        )

        if self.origin_vid != 0 or self.origin_pid != 0:
            output += (
                f"  DAC Origin Vendor ID: {self.origin_vid} (0x{self.origin_vid:X})\n"
                f"  DAC Origin Product ID: {self.origin_pid} (0x{self.origin_pid:X})\n"
            )

        if self.paa_authority_count > 0:
            output += (
                f"  Authorized PAA List: {authorized_paa_list_str}\n"
                f"  Authorized PAA List Count: {self.paa_authority_count}\n"
            )

        return output

    def to_ascii_table(self, alignment='l'):
        table = PrettyTable()
        table.field_names = ["Element", "Raw Value", "Pretty Value"]

        table.add_row(["Format Version", self.format_version, f"0x{self.format_version:X}"])
        table.add_row(["Vendor ID", self.vendor_id, f"0x{self.vendor_id:X}"])

        for idx, pid in enumerate(self.product_id_array):
            table.add_row([f"Product ID {idx + 1}", pid, f"0x{pid:X}"])

        table.add_row(["Product IDs Count", self.product_ids_count, f"0x{self.product_ids_count:X}"])
        table.add_row(["Device Type ID", self.device_type_id, f"0x{self.device_type_id:X}"])
        table.add_row(["Certificate ID", self.certificate_id, ""])
        table.add_row(["Security Level", self.security_level, f"0x{self.security_level:X}"])
        table.add_row(["Security Information", self.security_info, f"0x{self.security_info:X}"])
        table.add_row(["Version Number", self.version_number, f"0x{self.version_number:X}"])
        table.add_row(["Certification Type", self.certification_type, f"0x{self.certification_type:X}"])

        if self.origin_vid != 0 or self.origin_pid != 0:
            table.add_row(["DAC Origin Vendor ID", self.origin_vid, f"0x{self.origin_vid:X}"])
            table.add_row(["DAC Origin Product ID", self.origin_pid, f"0x{self.origin_pid:X}"])

        if self.paa_authority_count > 0:
            for idx, paa in enumerate(self.paa_authority_list, ):
                if idx < len(self._paa_authority_list_name):
                    table.add_row([f"Authorized PAA {idx + 1}", paa.hex().upper(), self._paa_authority_list_name[idx]])
                else:
                    table.add_row([f"Authorized PAA {idx + 1}", paa.hex().upper(), ""])
            table.add_row(["Authorized PAA List Count", self.paa_authority_count, f"0x{self.paa_authority_count:X}"])

        if alignment == 'c':
            table.align = 'c'
        else:
            table.align = 'l'

        return table

    def append_paa_authority_list_name(self, paa_name):
        self._paa_authority_list_name.append(paa_name)
