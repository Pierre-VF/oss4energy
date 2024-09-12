import os
from ftplib import FTP

from oss4energy.config import SETTINGS
from oss4energy.log import log_info

assert SETTINGS.EXPORT_FTP_URL is not None, "URL must be defined for this to work"
assert SETTINGS.EXPORT_FTP_USER is not None, "Username must be defined for this to work"
assert (
    SETTINGS.EXPORT_FTP_PASSWORD is not None
), "Password must be defined for this to work"

files_out = [
    ".data/summary.toml",
    ".data/listing_data.csv",
]

with FTP(
    host=SETTINGS.EXPORT_FTP_URL,
    user=SETTINGS.EXPORT_FTP_USER,
    passwd=SETTINGS.EXPORT_FTP_PASSWORD,
) as ftp:
    try:
        ftp.mkd("oss4energy")
    except:
        pass
    ftp.cwd("oss4energy")
    for i in files_out:
        with open(i, "rb") as fp:
            log_info(f"Uploading {i}")
            ftp.storbinary("STOR %s" % os.path.basename(i), fp, blocksize=1024)
