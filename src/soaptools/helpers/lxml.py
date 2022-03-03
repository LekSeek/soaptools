from typing import Dict

def get_full_identifier(val: str, nsmap: Dict[str, str]) -> str:
    if ":" in val:
        ns_prefix, node_name = val.split(":")
        val = "{%s}%s" % (nsmap[ns_prefix], node_name)
    return val


def xml_val_to_python_val(val: str):
    if val == "true":
        return True
    if val == "false":
        return False
    if val.isdigit():
        return int(val)

    return val
