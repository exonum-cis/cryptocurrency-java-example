"""Example of sending transactions for cryptocurrency.
Before running this script ensure that `cryptocurrency` service
is deployed and started.
The name of the instance is expected to be `cryptocurrency` by default,
otherwise edit the CRYPTOCURRENCY_INSTANCE_NAME constant."""

from typing import Any, Tuple
import requests
import random
from exonum_client_cis import ExonumClient, ModuleManager, MessageGenerator
from exonum_client_cis.api import Api
from exonum_client_cis.crypto import KeyPair, PublicKey

JAVA_RUNTIME_ID = 1
SUPERVISOR_ARTIFACT_NAME = "exonum-supervisor:0.13.0-rc.2"
CRYPTOCURRENCY_ARTIFACT = "com.exonum.binding:exonum-java-binding-cryptocurrency-demo:0.9.0-rc2-cis"
CRYPTOCURRENCY_INSTANCE_NAME = "cryptocurrency"
DEFAULT_CHANNEL_ID = 0
SERVICE_PROTO_DIR = "../../src/main/proto"

class JavaRuntimeApi(Api):
    """Api class provides methods to interact with the public API of an Java runtime."""
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.base_url = self.endpoint_prefix + "/services"

    def instance_url(self, instance_name: str):
        instance_url = "{}/{}".format(self.base_url, instance_name)
        return instance_url


def run() -> None:
    """This example creates two wallets (for Alice and Bob) and performs several
    transactions between these wallets."""
    hostname = "127.0.0.1"
    java_runtime_api_port = 7000
    client = ExonumClient(hostname, public_api_port=3000, private_api_port=3010)
    java_runtime_api = JavaRuntimeApi(hostname, java_runtime_api_port, "http")

    with client.protobuf_loader() as loader:
        # Load and compile proto files:
        loader.load_main_proto_files()
        loader.compile_service_proto_files_from_dir(SERVICE_PROTO_DIR, JAVA_RUNTIME_ID, CRYPTOCURRENCY_ARTIFACT)

        instance_id = get_cryptocurrency_instance_id(client)
        cryptocurrency_message_generator = MessageGenerator(
            instance_id, "com.exonum.binding:exonum-java-binding-cryptocurrency-demo:0.9.0-rc2-cis"
        )

        alice_keypair = create_wallet(client, cryptocurrency_message_generator, "Alice")
        bob_keypair = create_wallet(client, cryptocurrency_message_generator, "Bob")

        alice_balance = get_balance(java_runtime_api, alice_keypair.public_key)
        bob_balance = get_balance(java_runtime_api, bob_keypair.public_key)
        print("Created the wallets for Alice and Bob. Balance:")
        print(f" Alice => {alice_balance}")
        print(f" Bob => {bob_balance}")

        amount = random.randint(0, 100)
        alice_balance, bob_balance = transfer(
            client, java_runtime_api, cryptocurrency_message_generator, alice_keypair, bob_keypair.public_key, amount
        )

        print(f"Transferred {amount} tokens from Alice's wallet to Bob's one")
        print(f" Alice => {alice_balance}")
        print(f" Bob => {bob_balance}")

        amount = 25
        bob_balance, alice_balance = transfer(
            client, java_runtime_api, cryptocurrency_message_generator, bob_keypair, alice_keypair.public_key, amount
        )

        print(f"Transferred {amount} tokens from Bob's wallet to Alice's one")
        print(f" Alice => {alice_balance}")
        print(f" Bob => {bob_balance}")


def get_cryptocurrency_instance_id(client: ExonumClient) -> int:
    """Ensures that the service is added to the running instances list and gets
    the ID of the instance."""
    instance_name = CRYPTOCURRENCY_INSTANCE_NAME
    available_services = client.public_api.available_services().json()
    if instance_name not in map(lambda x: x["spec"]["name"], available_services["services"]):
        raise RuntimeError(f"{instance_name} is not listed in the running instances after the start")

    # Service starts.
    # Return the running instance ID:
    for instance in available_services["services"]:
        if instance["spec"]["name"] == instance_name:
            return instance["spec"]["id"]

    raise RuntimeError("Instance ID was not found")


def create_wallet(client: ExonumClient, message_generator: MessageGenerator, name: str) -> KeyPair:
    """Creates a wallet with the given name and returns a KeyPair for it."""
    key_pair = KeyPair.generate()

    # Load the "service.proto" from the Cryptocurrency service:
    cryptocurrency_module = ModuleManager.import_service_module(
        CRYPTOCURRENCY_ARTIFACT, "service"
    )

    # Create a Protobuf message:
    create_wallet_message = cryptocurrency_module.CreateWalletTx()
    create_wallet_message.initialBalance = random.randint(100, 1000)

    # Convert the Protobuf message to an Exonum message and sign it:
    create_wallet_tx = message_generator.create_message(create_wallet_message)
    create_wallet_tx.sign(DEFAULT_CHANNEL_ID, key_pair)

    # Send the transaction to Exonum:
    response = client.public_api.send_transaction(create_wallet_tx)
    ensure_status_code(response)
    tx_hash = response.json()["tx_hash"]
    print(f"Create wallet transaction hash: {tx_hash}")

    # Wait for new blocks:
    with client.create_subscriber("blocks") as subscriber:
        subscriber.wait_for_new_event()
        subscriber.wait_for_new_event()

    ensure_transaction_success(client, tx_hash)

    print(f"Successfully created wallet with name '{name}'")

    return key_pair


def transfer(
        client: ExonumClient, java_runtime_api: JavaRuntimeApi,
        message_generator: MessageGenerator, from_keypair: KeyPair, to_key: PublicKey, amount: int
) -> Tuple[int, int]:
    """This example transfers tokens from one wallet to the other one and
    returns the balances of these wallets."""

    cryptocurrency_module = ModuleManager.import_service_module(
        CRYPTOCURRENCY_ARTIFACT, "service"
    )

    transfer_message = cryptocurrency_module.TransferTx()
    transfer_message.toWallet = bytes.fromhex(to_key.hex())
    transfer_message.sum = amount
    transfer_message.seed = Seed.get_seed()

    transfer_tx = message_generator.create_message(transfer_message)
    transfer_tx.sign(0, from_keypair)

    response = client.public_api.send_transaction(transfer_tx)
    ensure_status_code(response)
    tx_hash = response.json()["tx_hash"]
    print(f"Transfer transaction hash: {tx_hash}")

    # Wait for new blocks:

    with client.create_subscriber("blocks") as subscriber:
        subscriber.wait_for_new_event()
        subscriber.wait_for_new_event()

    ensure_transaction_success(client, tx_hash)

    from_balance = get_balance(java_runtime_api, from_keypair.public_key)
    to_balance = get_balance(java_runtime_api, to_key)

    return from_balance, to_balance


def get_balance(runtime_api: JavaRuntimeApi, key: PublicKey) -> int:
    """The example returns the balance of the wallet."""
    url = "{}/wallet/{}".format(runtime_api.instance_url(CRYPTOCURRENCY_INSTANCE_NAME), key.hex())
    wallet_info = runtime_api.get(url)
    ensure_status_code(wallet_info)
    balance = wallet_info.json()["balance"]
    return balance


def ensure_status_code(response: requests.Response) -> None:
    """Raises an error if the status code is not 200."""
    if response.status_code != 200:
        raise RuntimeError(f"Received non-ok response: {response.content!r}")


def ensure_transaction_success(client: ExonumClient, tx_hash: str) -> None:
    """Checks that the transaction is committed and the status is success."""
    tx_info_response = client.public_api.get_tx_info(tx_hash)
    ensure_status_code(tx_info_response)

    tx_info = tx_info_response.json()
    if not (tx_info["type"] == "committed" and tx_info["status"]["type"] == "success"):
        raise RuntimeError(f"Error occured during transaction execution: {tx_info}")


class Seed:
    """Class that creates a new seed for each call."""

    seed = 1

    @classmethod
    def get_seed(cls) -> int:
        """Returns a new seed."""
        old_seed = cls.seed
        cls.seed += 1
        return old_seed


if __name__ == "__main__":
    run()