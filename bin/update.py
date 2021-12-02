#!/usr/bin/env python
import sys
import dotenv
from functools import reduce
import requests


def cmp_version(lhs, rhs):
    lhs_split = lhs.replace('-pre', '.').split(".")
    rhs_split = rhs.replace('-pre', '.').split(".")
    i = 0
    while i < len(lhs_split) and i < len(rhs_split):
        rhs_v = int(rhs_split[i])
        lhs_v = int(lhs_split[i])
        if rhs_v > lhs_v:
            return True
        elif rhs_v < lhs_v:
            return False
        i = i + 1
    return False


def higher_version(lhs, rhs):
    rhs_is_greater = cmp_version(lhs, rhs)
    if rhs_is_greater:
        return rhs
    else:
        return lhs


def higher_build(lhs, rhs):
    if int(rhs) > int(lhs):
        return rhs
    else:
        return lhs


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
v_req = requests.get("https://papermc.io/api/v2/projects/paper")
if v_req.status_code == 200:
    v_data = v_req.json()
    highest_version = reduce(lambda acc, cur: higher_version(acc, cur), v_data["versions"])
    print(f"Latest version found: {highest_version}")
    b_req = requests.get(f"https://papermc.io/api/v2/projects/paper/versions/{highest_version}")
    if b_req.status_code == 200:
        b_data = b_req.json()
        highest_build = reduce(lambda acc, cur: higher_build(acc, cur), b_data["builds"])
        print(f"Latest build found for {highest_version}: {highest_build}")
        f_req = requests.get(f"https://papermc.io/api/v2/projects/paper/versions/{highest_version}/builds/{highest_build}")
        if f_req.status_code == 200:
            f_data = f_req.json()
            filename = f_data["downloads"]["application"]["name"]
            sha256 = f_data["downloads"]["application"]["sha256"]
            print(f"Filename for {highest_version}-{highest_build}: {filename}")
            print(f"SHA256 hash for {filename}: {sha256}")
            prior_values = dotenv.dotenv_values()
            prior_version = prior_values.get("PAPER_VERSION", False) or "undefined"
            prior_build = prior_values.get("PAPER_BUILD", False) or "undefined"
            prior_filename = prior_values.get("PAPER_FILENAME", False) or "undefined"
            prior_sha256 = prior_values.get("PAPER_SHA256", False) or "undefined"
            print(f"Updating .env file ({dotenv_file})...")
            dotenv.set_key(dotenv_file, "PAPER_VERSION", str(highest_version))
            dotenv.set_key(dotenv_file, "PAPER_BUILD", str(highest_build))
            dotenv.set_key(dotenv_file, "PAPER_FILENAME", str(filename))
            dotenv.set_key(dotenv_file, "PAPER_SHA256", str(sha256))
            print("Updated:")
            print(f"PAPER_VERSION: {prior_version} -> {highest_version}")
            print(f"PAPER_BUILD: {prior_build} -> {highest_build}")
            print(f"PAPER_FILENAME: {prior_filename} -> {filename}")
            print(f"PAPER_SHA256: {prior_sha256} -> {sha256}")
        else:
            print("ERROR: Failed to fetch downloadable files from Paper API", file=sys.stderr)
            exit(1)
    else:
        print("ERROR: Failed to fetch builds from Paper API", file=sys.stderr)
        exit(1)
else:
    print("ERROR: Failed to fetch versions from Paper API", file=sys.stderr)
    exit(1)
