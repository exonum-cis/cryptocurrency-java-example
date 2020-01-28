(function () {
    "use strict";

    // Imports
    const exonum = require("exonum-client-cis");
    const proto = require("./proto/stubs.js");

    // Choose crypto-algorithm.
    // noinspection JSUnresolvedVariable
    exonum.CONFIG.crypto = exonum.CRYPTO.NIST;

    // Subchain identifier.
    const CHAIN_ID = 0;

    // Service instance identifiers.
    const CRYPTOCURRENCY_INSTANCE_ID = 2;

    // Method identifiers for creating wallet and transfer coins.
    const CC_CREATE_WALLET_METHOD_ID = 1;
    const CC_TRANSFER_METHOD_ID = 2;

    // Globals
    const EXPLORER_BASE_PATH = "http://127.0.0.1:3000/api/explorer/v1/transactions";
    const SEND_ATTEMPTS = 100;
    const SEND_TIMEOUT = 500;
    const keyPairAlice = {
        "publicKey": "f930e9c2186718b8bee562a53a2b78a91862ef1e2a0fed58e5afd34c04b1d1c8",
        "secretKey": "ee08ca60d2f80ac59ac91f1c8447269ad53183461ef01b58f8113342c29d8363f930e9c2186718b8bee562a53a2b78a91862ef1e2a0fed58e5afd34c04b1d1c8"
    };
    const keyPairBob = {
        "publicKey": "c1c92437490881703958fbdc3f9f6f20a3530ee3f1c3203b99f7465941fcc805",
        "secretKey": "b8a03b6b10ee1ac84efab00a40dce82976034b0f51547f63af6074e026796355c1c92437490881703958fbdc3f9f6f20a3530ee3f1c3203b99f7465941fcc805"
    };

    // Log
    const log = {
        error: function (message) {
            console.log("↳ ERROR! " + message);
        },
        info: function (message) {
            console.log(message);
        }
    };

    // Transactions
    let txs = [];
    txs["CreateWalletAlice"] = new exonum.Transaction({
        chainId: CHAIN_ID,
        serviceId: CRYPTOCURRENCY_INSTANCE_ID,
        methodId: CC_CREATE_WALLET_METHOD_ID,
        schema: proto.CreateWalletTx,
    });
    txs["CreateWalletBob"] = new exonum.Transaction({
        chainId: CHAIN_ID,
        serviceId: CRYPTOCURRENCY_INSTANCE_ID,
        methodId: CC_CREATE_WALLET_METHOD_ID,
        schema: proto.CreateWalletTx,
    });
    txs["TransferTx"] = new exonum.Transaction({
        chainId: CHAIN_ID,
        serviceId: CRYPTOCURRENCY_INSTANCE_ID,
        methodId: CC_TRANSFER_METHOD_ID,
        schema: proto.TransferTx,
    });

    async function sendTransaction(txName, txData, keyPair) {
        let signed = await txs[txName].create(txData, keyPair);
        const txHash = await exonum.send(EXPLORER_BASE_PATH, signed.serialize())
        log.info("↳ OK! " + txHash);
    }

    // Test transaction
    const txQueue = [
        {
            name: "CreateWalletAlice",
            data: {
                initialBalance: 100,
            },
            keyPair: keyPairAlice,
        },
        {
            name: "CreateWalletBob",
            data: {
                initialBalance: 50,
            },
            keyPair: keyPairBob,
        },
        {
            name: "TransferTx",
            data: {
                seed: "123",
                toWallet: exonum.hexadecimalToUint8Array(keyPairBob.publicKey),
                sum: 20
            },
            keyPair: keyPairAlice,
        }
    ];

    let executeTransactions = async () => {
        for (let tx of txQueue) {
            await sendTransaction(tx.name, tx.data, tx.keyPair);
        }
    };

    executeTransactions()
        .catch((reason) => {
            log.error(reason);
            process.exit(1);
        });

}());