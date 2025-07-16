from ._types import PIAConnectionState, PIAInformationType, PIAPortForwardStatus, PIAProtocol

import ipaddress

def string_to_bool(string: str) -> bool:
    return string == 'true'

def is_integer(string: str) -> bool:
    try:
        int(string)
        return True
    except Exception:
        return False

def is_ipv4(string: str) -> bool:
    try:
        ipaddress.IPv4Address(string)
        return True
    except Exception:
        return False

def parse(raw_data: str, type: PIAInformationType):
    match type:
        case PIAInformationType.ALLOW_LAN | \
             PIAInformationType.DEBUG_LOGGING | \
             PIAInformationType.REQUEST_PORT_FORWARD:
            return string_to_bool(raw_data)
        case PIAInformationType.CONNECTION_STATE:
            return PIAConnectionState.from_value(raw_data)
        case PIAInformationType.PORT_FORWARD:
            if is_integer(raw_data):
                return int(raw_data)
            else:
                return PIAPortForwardStatus.from_value(raw_data)
        case PIAInformationType.PROTOCOL:
            return PIAProtocol.from_value(raw_data)
        case PIAInformationType.PUB_IP | \
             PIAInformationType.VPN_IP:
            return raw_data if is_ipv4(raw_data) else None
        case PIAInformationType.REGION:
            return raw_data
        case PIAInformationType.REGIONS:
            return set(raw_data.splitlines())
        case _:
            return None
