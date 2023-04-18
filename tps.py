#!/usr/bin/env python3
# from __future__ import print_function




import time, timeit, sys, os

from web3 import Web3, HTTPProvider

from config import RPCaddress2 #, RAFT
from deploy import loadFromDisk, CONTRACT_ADDRESS
from clienttools import web3connection
    

def loopUntilActionBegins_raft(blockNumber_start, query_intervall = 0.1):
    while(True):
        blockNumber=w3.eth.blockNumber
        if (blockNumber != blockNumber_start):
            break
        time.sleep(query_intervall)
    print('')
    return blockNumber_start + 1


def loopUntilActionBegins_withNewContract(blockNumber_start, query_intervall = 0.1):
    address, _ = loadFromDisk()
    when = os.path.getmtime(CONTRACT_ADDRESS) 
    print ("(filedate %d) last contract address: %s" %(when, address))
    while(True):
        time.sleep(query_intervall)
        newAddress, _ = loadFromDisk()
        newWhen = os.path.getmtime(CONTRACT_ADDRESS)
        if (newAddress != address or newWhen != when):
            print ("(filedate %d) new contract address: %s" %(newWhen, newAddress))  
            break
    print('')
    return w3.eth.blockNumber



def loopUntilActionBegins_OBSOLETE(blockNumber_start, query_intervall = 0.1):
    if RAFT: # TODO - automate that hardcoded constant away with CONSENSUS query result  
        return loopUntilActionBegins_raft(blockNumber_start, query_intervall=query_intervall)
    else:
        return loopUntilActionBegins_withNewContract(blockNumber_start, query_intervall=query_intervall)


def loopUntilActionBegins(blockNumber_start, query_intervall = 0.1):
    return loopUntilActionBegins_withNewContract(blockNumber_start, query_intervall=query_intervall)



def analyzeNewBlocks(blockNumber, newBlockNumber, txCount, start_time):
    txCount_new = 0
    for bl in range(blockNumber+1, newBlockNumber+1):
        txCount_new += w3.eth.getBlockTransactionCount(bl)

    ts_blockNumber =    w3.eth.getBlock(   blockNumber).timestamp
    ts_newBlockNumber = w3.eth.getBlock(newBlockNumber).timestamp
    timeunits = 1000000000.0 if CONSENSUS=="raft" else 1.0
    
    blocktimeSeconds = (ts_newBlockNumber - ts_blockNumber) / timeunits
    
    try:
        tps_current = txCount_new / blocktimeSeconds
    except ZeroDivisionError:
        tps_current = 0
    txCount += txCount_new
    elapsed = timeit.default_timer() - start_time
    tps = txCount / elapsed
    line = "block %d | new #TX %3d / %4.0f ms = %5.1f TPS_current | total: #TX %4d / %4.1f s = %5.1f TPS_average" 
    line = line % ( blockNumber, txCount_new, blocktimeSeconds * 1000, tps_current, txCount, elapsed, tps) 
    print (line)
    return txCount


def measurement(blockNumber, pauseBetweenQueries=0.3):
    txCount=w3.eth.getBlockTransactionCount(blockNumber)
    start_time = timeit.default_timer()
    print('starting timer, at block', blockNumber, 'which has ', txCount,' transactions; at timecode', start_time)
    while(True):
        newBlockNumber=w3.eth.blockNumber
        if(blockNumber!=newBlockNumber):
            txCount = analyzeNewBlocks(blockNumber, newBlockNumber, txCount, start_time)
            blockNumber = newBlockNumber
        time.sleep(pauseBetweenQueries)
    print ("end")


if __name__ == '__main__':
    
    global w3, NODENAME, NODETYPE, CONSENSUS, NETWORKID, CHAINNAME, CHAINID
    w3, chainInfos = web3connection(RPCaddress=RPCaddress2, account=None)
    NODENAME, NODETYPE, CONSENSUS, NETWORKID, CHAINNAME, CHAINID = chainInfos
    blockNumber_start = w3.eth.blockNumber
    print ("\nBlock ",blockNumber_start," - waiting for something to happen")
    blocknumber_start_here = loopUntilActionBegins(blockNumber_start) 
    print ("blocknumber_start_here =", blocknumber_start_here)
    measurement( blocknumber_start_here )
    
    