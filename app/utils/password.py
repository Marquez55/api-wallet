import re


def valid_password(p):
    return len(p) > 6
    # x = True
    # while x:
    # 	if (len(p) <6 or len(p) > 12):
    # 		break
    # 	elif not re.search("[a-z]",p):
    # 		break
    # 	elif not re.search("[0-9]",p):
    # 		break
    # 	elif not re.search("[A-Z]",p):
    # 		break
    # 	elif not re.search("[$#@._-]",p):
    # 		break
    # 	elif re.search("\s",p):
    # 		break
    # 	else:
    # 		return True
    # 		break

    # if x:
    # 	return False
