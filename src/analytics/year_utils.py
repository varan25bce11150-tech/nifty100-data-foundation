import re

def extract_year(value):
    """
    Converts:
        Dec 2012 -> 2012
        Mar 2014 -> 2014
        Mar-13   -> 2013
        2015     -> 2015
    """

    if value is None:
        return None

    text = str(value)

    # 4-digit year
    m = re.search(r"(19|20)\d{2}", text)
    if m:
        return int(m.group())

    # 2-digit year (Mar-13)
    m = re.search(r"-(\d{2})$", text)

    if m:
        y = int(m.group(1))

        if y <= 30:
            return 2000 + y

        return 1900 + y

    return None