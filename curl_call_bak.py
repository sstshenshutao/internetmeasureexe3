import json
import subprocess
import shlex
import logging

# sources = [
#     "https://quic.tech:8443/"
# ]
sources = [
    "https://pgjones.dev",
    "https://github.com/aiortc/aioquic",
    "https://quic.tech:8443/",
    "https://github.com/cloudflare/quiche",
    "https://fb.mvfst.net:4433/",
    "https://github.com/facebookincubator/mvfst",
    "https://quic.rocks:4433/",
    "https://quiche.googlesource.com/quiche/",
    "https://f5quic.com:4433/",
    "https://www.litespeedtech.com",
    "https://github.com/litespeedtech/lsquic",
    "https://nghttp2.org:4433/",
    "https://github.com/ngtcp2/ngtcp2",
    "https://test.privateoctopus.com:4433/",
    "https://github.com/private-octopus/picoquic",
    "https://h2o.examp1e.net",
    "https://quic.westus.cloudapp.azure.com",
    "https://docs.trafficserver.apache.org/en/latest/"
]
curl_program = "./build_curl/curl/src/curl"

wflag="-w 'time_appconnect: %{time_appconnect}\ntime_connect: %{time_connect}\ntime_namelookup: %{time_namelookup}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect: %{time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\nremote_ip: %{remote_ip}\nremote_port: %{remote_port}\n'"

# create logger with 'spam_application'
logger = logging.getLogger('curl_return')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('curl_return.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


# url = "https://quic.rocks:4433/"
# url = "https://www.baidu.com/"
def call_curl(url, timeout_second, mode='header'):
    if mode == 'header':
        command = "%s -ilv %s --http3 --connect-timeout %d" % (curl_program, url, timeout_second)
    else:
        command = "%s -ilv %s --http3 --connect-timeout %d" % (curl_program, url, timeout_second)
    split_command = shlex.split(command)
    # print(split_command)
    proc = subprocess.Popen(split_command,
                            stdout=subprocess.PIPE)
    try:
        stdout, _ = proc.communicate(timeout=timeout_second)
        print(stdout)
    except subprocess.TimeoutExpired:
        return [None, True]
    return [stdout.decode('utf-8'), False]


def to_file(filename, str):
    f = open(filename, "a")
    f.write(str)
    f.close()


# test
# ret, err = call_curl(sources[0], timeout_second=5)
# if not err:
#     to_file("curl_out.txt", ret)
def parse_alt_svc(line):
    attrs = line[line.index('alt-svc:') + len('alt-svc:'):].strip()
    support_version = []
    for attr in attrs.split(';'):
        key = attr[:attr.index('=')].strip()
        if 'h3-' in key:
            version_index = key.index('-')
            if version_index > -1:
                support_version.append({
                    "version": key[version_index + 1:],
                    "alt_authority": attr[attr.index('=') + 2:-1].strip()
                })
    return support_version


def parse_curl_return(ret_str, err, url, tried=False):
    def full_mode_call():
        if tried:
            logger.warning("url: %s, \n %s" % (url, ret_str))
            return ['error', None]
        else:
            # the header mode may be not accepted by the server, use the full connection:
            return parse_curl_return(*call_curl(url, 10, mode='full'), url, tried=True)

    # timeout:
    if err:
        return ['timeout', None]
    # connection refused:
    if len(ret_str) == 0:
        return ['connection refused', None]
    # parse the returned header
    str_arr = ret_str.split('\n')
    if "HTTP/3" in str_arr[0]:
        # get the code:
        code = str_arr[0][len("HTTP/3") + 1:]
        if code != '200':
            return full_mode_call()
        # try to fine the h3-version 
        for line in str_arr:
            pure_line = line.strip()
            if pure_line.startswith('alt-svc:'):
                return ['ok', parse_alt_svc(pure_line)]
    else:
        return full_mode_call()


# alt-svc: h3-28=":443"; ma=3600
# Alt-Svc: <protocol-id>=<alt-authority>; ma=<max-age>; persist=1


for url in sources:
    ret = parse_curl_return(*call_curl(url, timeout_second=5), url=url)
    json_ret = json.dumps(ret, sort_keys=True, indent=4)
    to_file("curl_out.txt", json_ret)
