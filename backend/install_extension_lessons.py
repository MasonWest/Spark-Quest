"""Dry-run by default; --apply backs up and atomically adds both lessons and pools."""
import argparse
import json
from app.database import engine
from app.course_extensions import install

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true')
    print(json.dumps(install(engine,parser.parse_args().apply),ensure_ascii=False))
