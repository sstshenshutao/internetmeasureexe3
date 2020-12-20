import os

import pyasn
from pyasn import mrtx
from utils import ipasn_db, bgp_rib, asn_regex_csv, asns_csv
import pandas as pd


# converting MRT/RIB archives to IPASN databases.
def convert(src, dist):
    print('WAIT: converting MRT/RIB archives to IPASN databases.')
    prefixes = mrtx.parse_mrt_file(src, print_progress=True,
                                   skip_record_on_error=True)
    mrtx.dump_prefixes_to_file(prefixes, dist, src)
    v6 = sum(1 for x in prefixes if ':' in x)
    v4 = len(prefixes) - v6
    print('IPASN database saved (%d IPV4 + %d IPV6 prefixes)' % (v4, v6))


class Asn:

    def __init__(self):
        self._asndb = self.prepare_databases()

    def prepare_databases(self):
        if not os.path.exists(ipasn_db):
            convert(src=bgp_rib, dist=ipasn_db)
        # load the asn dat file
        return pyasn.pyasn(ipasn_db)

    def lookup(self, ip_address):
        return self._asndb.lookup(ip_address)[0]


class Host:
    def __init__(self):
        # self._init_re_rules()
        self._init_asns_rules()

    # def _init_re_rules(self):
    #     with open(asn_regex_csv) as f:
    #         content = f.readlines()
    #     re_list = []
    #     for c in content:
    #         exec("re_list.append(" + c[:len(c) - 1] + ')')
    #     self.re_list = re_list

    def _init_asns_rules(self):
        df = pd.read_csv(asns_csv, sep=";")
        self.asns = df[['provider', 'asn']].drop_duplicates()

    def identify_ases(self, ases):
        search_df = self.asns.loc[self.asns['asn'] == ases]
        if search_df.empty:
            return None
        else:
            return search_df['provider'].values[0]

    # def identify_cname(self, response_name):
    #     for i in range(len(self.re_list)):
    #         if self.re_list[i][1].match(response_name) is not None:
    #             return self.re_list[i][0]
    #     return None
