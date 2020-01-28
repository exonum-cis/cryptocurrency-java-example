# JS Light client example for cryptocurrency service

## Install
Install exonum-client-cis from pip3:
```aidl
pip3 install exonum-client-cis
```

## Requirements
- Node 10+

# Build
Run:
```bash
npm run build
```

## Run
1. Start node with bash script:
```bash
bash start-node.sh
```
2. Deploy service:
```bash
python3 -m exonum_launcher -i cryptocurrency-demo.yml
```
3. Run JS example script
```bash
node index.js
```