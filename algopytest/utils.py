import base64
from typing import Any, Dict, List, Optional

from algosdk.encoding import encode_address


def _base64_to_str(b64: str) -> str:
    """Converts a b64 encoded string to a normal UTF-8 string."""
    # Decode the base64 to bytes and then decode them as a UTF-8 string
    byte_decoding = base64.b64decode(b64)
    return byte_decoding.decode("utf-8")


def _convert_algo_dict(
    algo_dict: List[Dict[str, Any]], address_fields: Optional[List[str]]
) -> Dict[str, str]:
    """Converts an Algorand dictionary to a Python one."""
    # Materialize the `address_fields` to a list type
    address_fields = address_fields or []

    ret = {}
    for entry in algo_dict:
        key = _base64_to_str(entry["key"])

        value_type = entry["value"]["type"]

        if value_type == 1 and key not in address_fields:  # Bytes non-address
            value = _base64_to_str(entry["value"]["bytes"])
        elif value_type == 1 and key in address_fields:  # Bytes address
            value = encode_address(base64.b64decode(entry["value"]["bytes"]))
        elif value_type == 2:  # Integer
            value = entry["value"]["uint"]
        else:
            raise ValueError(f"Unknown value type for key: {key}")

        ret[key] = value

    return ret
