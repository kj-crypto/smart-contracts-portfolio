import requests
from eth_abi import encode_abi

EXPLORER_URL = "http://localhost:4000"


def publish(
    contract: "ContractContainer", contract_address: str, *constructor_arguments  # noqa
):
    """Publish contract to blockscout explorer running locally"""
    info = contract.get_verification_info()
    version = info["compiler_version"]
    version = version[: version.find("+")]
    standard_json = info["standard_json_input"]

    # ?module=contract&action=verifysourcecode&codeformat={solidity-standard-json-input}&contractaddress={contractaddress}&contractname={contractname}&compilerversion={compilerversion}&sourceCode={sourceCode}
    data = {
        "codeFormat": "solidity-standard-json-input",
        "contractAddress": contract_address,
        "contractName": info["contract_name"],
        "compilerVersion": version,
        "sourceCode": standard_json,
        "constructorArguments": encode_constructor(
            contract.abi, *constructor_arguments
        ).hex()
        if constructor_arguments
        else "",
    }

    try:
        print("Source code publishing ...")
        response = requests.post(
            url=f"{EXPLORER_URL}/api?module=contract&action=verifySourceCode",
            json=data,
            timeout=120,
        )
        if response.status_code != 200:
            print("Error !!", response.status_code)
        print(response.json())
    except Exception as e:
        print("Error !!", e)


def encode_constructor(abi: dict, *args) -> bytes:
    input_types = [
        input["type"]
        for abi_item in abi
        if abi_item.get("name", "") == abi_item.get("type", "") == "constructor"
        for input in abi_item["inputs"]
    ]
    return encode_abi(input_types, args)
