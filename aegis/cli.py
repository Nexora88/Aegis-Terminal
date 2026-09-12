import argparse,json
from .monitor import snapshot,processes,interfaces
from .integrity import sha256_file
from .decision import assess

def main():
 p=argparse.ArgumentParser(prog='aegis'); s=p.add_subparsers(dest='cmd')
 for x in ['system','processes','interfaces','assess']: s.add_parser(x)
 h=s.add_parser('hash'); h.add_argument('path')
 a=p.parse_args()
 if a.cmd=='system': d=snapshot()
 elif a.cmd=='processes': d=processes()
 elif a.cmd=='interfaces': d=interfaces()
 elif a.cmd=='assess': d=assess(snapshot())
 elif a.cmd=='hash': d=sha256_file(a.path)
 else: p.print_help(); return
 print(json.dumps(d,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
