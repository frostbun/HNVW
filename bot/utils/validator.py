from requests import head

def check_url(url):
    try: return head(url).status_code < 400
    except Exception: return False
