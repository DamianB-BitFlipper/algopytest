import base64

import algosdk
import pytest

from algopytest.utils import _base64_to_str, _convert_algo_dict


def test_base64_to_str():
    b64 = b"TmV2ZXIgR29ubmEgR2l2ZSBZb3UgVXAh"
    assert _base64_to_str(b64) == "Never Gonna Give You Up!"


@pytest.mark.parametrize(
    "key,value,is_address",
    [
        ("Buyer", "Damian Barabonkov", False),
        (
            "Payment-Addr",
            "3MFXIV56APKIGH3C4M3DX4RUAFKQ7CCCOVTQCW5GCTTHXHJ5C7OTWPDVAQ",
            True,
        ),
        ("Price", 42, False),
    ],
)
def test_convert_algo_dict(key, value, is_address):
    key_enc = base64.b64encode(bytes(key, "utf-8"))

    if is_address:
        bytes_value_enc = base64.b64encode(algosdk.encoding.decode_address(value))
        uint_value = 0
        value_type = 1
        address_fields = [key]
    elif isinstance(value, str):
        bytes_value_enc = base64.b64encode(bytes(value, "utf-8"))
        uint_value = 0
        value_type = 1
        address_fields = None
    else:
        bytes_value_enc = b""
        uint_value = value
        value_type = 2
        address_fields = None

    # Construct a dictionary entry representation of how state is stored in Algorand
    algo_dict = [
        {
            "key": key_enc,
            "value": {"bytes": bytes_value_enc, "type": value_type, "uint": uint_value},
        }
    ]
    print(algo_dict)

    # Convert the `algo_dict` to a regular Python dictionary
    python_dict = _convert_algo_dict(algo_dict, address_fields=address_fields)

    assert python_dict == {key: value}


def test_convert_algo_dict_raises():
    # Set an invalid value type
    invalid_algo_dict = [
        {
            "key": b"QnV5ZXI=",
            "value": {"bytes": b"RGFtaWFuIEJhcmFib25rb3Y=", "type": 3, "uint": 0},
        }
    ]

    with pytest.raises(ValueError, match="Unknown value type for key: Buyer"):
        _ = _convert_algo_dict(invalid_algo_dict, None)
