
1. 우분투 서버 패키지 & Venv 세팅
https://gitlab.com/electronDLT/chainhammer
sudo apt-get -y install python3-pip libssl-dev
sudo pip3 install virtualenv
virtualenv -p python3 py3eth
source py3eth/bin/activate

2. Python 패키지 설치
python3 -m pip install --upgrade pip==18.0
pip3 install --upgrade py-solc==2.1.0 web3==4.3.0 web3[tester]==4.3.0 rlp==0.6.0 eth-testrpc==1.3.4 requests pandas jupyter ipykernel matplotlib
ipython kernel install --user --name="Python.3.py3eth"

3. py-solc 설치
pip3 install solc-select
solc-select install {version}
solc-select use {version}

4. config.py에 RPC정보 입력

5. 실행
./deploy.py
터미널을 2개 열고
./tps.py (첫번째 터미널에서)
./deploy.py notest; ./send.py threaded2 23 (두번째 터미널에서)

6. jupyter notebook
cd chainreader
./blocksDB_create.py {allblocks-parity_run7.db}

jupyter notebook blocksDB_analyze_parity-aura_run7.ipynb --allow-root --ip=0.0.0.0
