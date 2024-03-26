from .helpers import read_json, read_txt

ACCOUNT_NAMES = read_txt("user_data/input_data/account_names.txt")

PRIVATE_KEYS = read_txt("user_data/input_data/private_keys.txt")

PROXIES = read_txt("user_data/input_data/proxies.txt")

RECIPIENTS = read_txt("user_data/input_data/recipients.txt")
