#!/usr/bin/env python3



################
## Dependencies:

import sys, time, json
from pprint import pprint

import requests # pip3 install requests

try:
    from web3 import Web3, HTTPProvider # pip3 install web3
    from solc import compile_source # pip install py-solc
except:
    print ("Dependencies unavailable. Start virtualenv first!")
    exit()

from config import RPCaddress, CONTRACT_SOURCE, CONTRACT_ABI, CONTRACT_ADDRESS
from config import PRIVATE_FOR, PASSPHRASE_FILE, PARITY_UNLOCK_EACH_TRANSACTION

from clienttools import web3connection, unlockAccount




def compileContract(contract_source_file):
    with open(contract_source_file, "r") as f:
        contract_source_code = f.read()
    compiled_sol = compile_source(contract_source_code) # Compiled source code
    assert(len(compiled_sol)==1) # assert source file has only one contract object
    contractName = list(compiled_sol.keys())[0] 
    contract_interface = compiled_sol[contractName]
    return contractName.replace("<stdin>:", ""), contract_interface 


def deployContract(contract_interface, ifPrint=True):
    myContract = w3.eth.contract(abi=contract_interface['abi'], 
                                 bytecode=contract_interface['bin'])
    tx_hash = w3.toHex( myContract.constructor().transact() )
    print ("tx_hash = ", tx_hash, "--> waiting for receipt ...")
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contractAddress = tx_receipt["contractAddress"]
    if ifPrint:
        print ( "Deployed. gasUsed={gasUsed} contractAddress={contractAddress}".format(**tx_receipt) )
    return contractAddress 

def contractObject(contractAddress, abi):
    myContract = w3.eth.contract(address=contractAddress,abi=abi)
    return myContract
    

##########################
## additional basic tasks:
##########################

def saveToDisk(contractAddress, abi):
    json.dump({"address": contractAddress}, open(CONTRACT_ADDRESS, 'w'))
    json.dump(abi, open(CONTRACT_ABI, 'w'))


def loadFromDisk():
    contractAddress = json.load(open(CONTRACT_ADDRESS, 'r'))
    abi = json.load(open(CONTRACT_ABI, 'r'))
    return contractAddress["address"], abi


def deployTheContract(contract_source_file):
    contractName, contract_interface = compileContract(contract_source_file)
    print ("unlock: ", unlockAccount())
    contractAddress = deployContract(contract_interface)
    saveToDisk(contractAddress, abi=contract_interface["abi"])
    return contractName, contract_interface, contractAddress


def testMethods(myContract):
    answer = myContract.functions.get().call()
    print('.get(): {}'.format(answer))
    
    if PARITY_UNLOCK_EACH_TRANSACTION:
        print ("unlockAccount:", unlockAccount())
    
    print('.set()')
    gas=90000
    txParameters = {'from': w3.eth.defaultAccount,
                    'gas' : gas}
    tx_hash = w3.toHex( myContract.functions.set(answer + 1).transact(txParameters) )
    print ("transaction", tx_hash, "... "); sys.stdout.flush()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print ("... mined. Receipt --> gasUsed={gasUsed}". format(**tx_receipt) )
    
    answer = myContract.functions.get().call()
    print('.get(): {}'.format(answer))



if __name__ == '__main__':
    global w3, NODENAME, NODETYPE, CONSENSUS, NETWORKID, CHAINNAME, CHAINID
    w3, chainInfos = web3connection(RPCaddress=RPCaddress, account=None)
    NODENAME, NODETYPE, CONSENSUS, NETWORKID, CHAINNAME, CHAINID = chainInfos
    deployTheContract(contract_source_file=CONTRACT_SOURCE)
    
    if len(sys.argv)>1 and sys.argv[1]=="notest":
        exit()
        
    contractAddress, abi = loadFromDisk()
    myContract = contractObject(contractAddress, abi)
    testMethods(myContract)
    
    
    
