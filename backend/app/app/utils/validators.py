import re


def check_nickname(cls, value) -> str | None:
    if value is None:
        return value
    print(cls, value)

    reg = re.compile(r"[가-힣a-zA-Z0-9_]+")

    if not reg.match(value):
        raise ValueError(
            "Nickname should have korean or english or number or underbar"
        )

    # korean : 2byte, english : 1byte, number : 1byte, underbar : 1byte
    # calculate byte length and check if under 16

    def korlen(str):
        korP = re.compile("[\u3131-\u3163\uAC00-\uD7A3]+", re.U)
        temp = re.findall(korP, str)
        temp_len = 0
        for item in temp:
            temp_len = temp_len + len(item)
        return len(str) + temp_len
    print(korlen(value), '1')
    if korlen(value) > 16:
        raise ValueError("Nickname should be under 16 bytes")

    return value


def check_password(cls, value) -> str | None:
    print(cls ,value)
    if value is None:
        return value
    
    
    passwordReg = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,20}$"
    
    if not re.match(passwordReg, value):
        raise ValueError("Password should have at least one number, one special character, one alphabet character")
    
    
    
    return value


def check_account_description(cls, value) -> str | None:
    if value is None:
        return value

    if len(value) > 100:
        raise ValueError("Description should be under 100 characters")

    return value