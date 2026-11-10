"""Install all L0-L7 purpose banks. Dry-run default; --apply backs up first."""
import argparse
import json
from install_reviewed_l3_l6 import install

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    print(json.dumps(install(parser.parse_args().apply)))
