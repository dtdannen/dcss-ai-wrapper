import os,sys
import json
from DCSSPDDLWriter import DCSSPDDLWriter

if len(sys.argv) < 2:
    print("   usage: dict_pddl.py <server messages>")
    os.exit(-1)

with open(sys.argv[1]) as f:
    server_str = f.read()
    msg_stream = json.loads(server_str)

pddlWriter = DCSSPDDLWriter()

for msgs in msg_stream:
    pddlWriter.hangleMessages( msgs )

pddlWriter.write_files( "domain.pddl", "problem.pddl" )

