import os

def is_bypassed() -> str | None:
    """
    Check if the CF_BYPASS_LOGIN environment variable is set
    """
    var = os.getenv("CF_BYPASS_LOGIN", None)
    if var is None:
        return None
    if (
        var.startswith("participant_0_")
        and var[-1].isdigit()
        and 0 <= int(var[-1]) <= 7
    ):
        return var
    return None
