# Copyright 2013 Setkeh Mkfr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.  See COPYING for more details.

#Short Python Example for connecting to The Cgminer API
#Written By: setkeh <https://github.com/setkeh>
#Thanks to Jezzz for all his Support.
#NOTE: When adding a param with a pipe | in bash or ZSH you must wrap the arg in quotes
#E.G "pga|0"
import uvicorn
import socket
import os
import json
import sys
import pprint
import datetime
import requests
import traceback
import requests
from sys import exc_info
pp = pprint.PrettyPrinter(indent=4)

from typing import Optional
import asyncio
from fastapi import FastAPI, Response
from metric import *

# if sys.platform == 'win32':
#     loop = asyncio.ProactorEventLoop()
#     asyncio.set_event_loop(loop)

app = FastAPI()
statusdata = {}
    



STORAGE = {}

AVAILABLE_COMMANDS = [ 'stats', 'version', 'pools', 'summary', 'devs' ]

export_metrics = {
    'summary': metric_summary,
    'pools': metric_pool,
    'stats': metric_stats
}

STORAGE = {}
try:
    with open('C:\\Monitoring\\creds.json') as f:
        CGI_LOGIN, CGI_PASSWORD = json.loads(f.read()).values()
except:
    CGI_LOGIN = None
    CGI_PASSWORD = None

def fetch_network_info(target):
    if CGI_LOGIN == None:
        STORAGE[target] = ("", "")
    if target not in STORAGE:
        url = "http://%s/cgi-bin/get_network_info.cgi"%target
        data = json.loads(requests.get(url, auth=requests.auth.HTTPDigestAuth(CGI_LOGIN, CGI_PASSWORD)).text)
        STORAGE[target] = (data["conf_hostname"], data["macaddr"]) 

    return STORAGE[target]

async def tcp_client(ip, command):
    data = b''
    reader, writer = await asyncio.open_connection(ip, 4028)

    writer.write(('{"command":"%s"}' % command).encode())
    await writer.drain()

    while True:
        chunk = await reader.read(100)
        if not chunk:
            break
        data += chunk
    return json.loads(data.decode().replace('\x00', '').replace('}{', '},{'))

async def fetch_metrics(ip, command):
    data = await tcp_client(ip, command)
    return (command, data)

@app.get("/")
def index():
    return Response("Use /metrics with ?target=IP\n")

@app.get("/api/{cmd}")
async def get_stats(cmd:str, target: str):
    if cmd in AVAILABLE_COMMANDS:
        text = await tcp_client(target, cmd)
        return text
    return {'error': 'unknown command'}

async def parse_tags(target, metricdata):
    if 'CGMiner' in metricdata['version']['VERSION'][0]:
        tags = 'instance="%s",cgminer_version="%s",api_version="%s",type="%s",miner="%s"'%(target,metricdata['version']['VERSION'][0]['CGMiner'],metricdata['version']['VERSION'][0]['API'],metricdata['version']['VERSION'][0]['Type'],metricdata['version']['VERSION'][0]['Miner'])
    elif 'BMMiner' in metricdata['version']['VERSION'][0]:
        tags = 'instance="%s",bmminer_version="%s",api_version="%s",type="%s",miner="%s"'%(target,metricdata['version']['VERSION'][0]['BMMiner'],metricdata['version']['VERSION'][0]['API'],metricdata['version']['VERSION'][0]['Type'],metricdata['version']['VERSION'][0]['Miner'])
    else:
        tags = 'instance="%s",api_version="%s",type="%s",miner="%s"'%(target, metricdata['version']['VERSION'][0]['API'],metricdata['version']['VERSION'][0]['Type'],metricdata['version']['VERSION'][0]['Miner'])
    
    if target not in STORAGE:
        hostname, mac = fetch_network_info(target)
    else:
        hostname, mac = STORAGE[target]
    tags+=',hostname="%s",mac="%s"'%(hostname, mac)
    return tags

@app.get("/metrics")
async def get_metrics(target: str):
    res = "#CGMiner metrics export\n"

    metric_data = dict(await asyncio.gather(
        *[fetch_metrics(target, cmd) for cmd in AVAILABLE_COMMANDS]
    ))
    
    tags = await parse_tags(target, metric_data)


    
    res+= "\n".join(
        await asyncio.gather(
            *[export_metrics[cmd](metric_data[cmd], tags) for cmd in export_metrics]
        )
    )

    return Response(res)
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9154, log_level="info")