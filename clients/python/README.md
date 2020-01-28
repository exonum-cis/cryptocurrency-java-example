# Python Light client example for cryptocurrency service

## Install
Install exonum-client-cis from pip3:
```aidl
pip3 install exonum-client-cis
```

## Run
1. Start node with bash script:
```aidl
bash start-node.sh
```
2. Deploy service:
```aidl
python3 -m exonum_launcher -i cryptocurrency-demo.yml
```
3. Run python example script
```aidl
python3 client.py
```