import brownie
from brownie import accounts, RandomNumberGenerator

def test_random_generator():
    # deploy contract
    random_generator = RandomNumberGenerator.deploy({'from': accounts[0]})

    text_message = 'some example text message'
    data = random_generator.getHash(text_message.encode('utf-8').hex(), {'from': accounts[0]})

    with brownie.reverts('Too small block number'):
        random_generator.commit(data, 0, {'from': accounts[0]})

    random_generator.commit(data, 2500, {'from': accounts[0]})
    commit = random_generator.commits(accounts[0].address, {'from': accounts[0]})
    assert commit[0] == data
    assert commit[1] == 2500
    assert commit[2] == False

    random_generator.commit(data, brownie.web3.eth.block_number + 1, {'from': accounts[0]})
    random_generator.generate({'from': accounts[0]})
    with brownie.reverts('Data already revealed'):
        random_generator.generate({'from': accounts[0]})

    results = []
    for _ in range(10):
        random_generator.commit(data, brownie.web3.eth.block_number + 1, {'from': accounts[0]})
        tx = random_generator.generate({'from': accounts[0]})
        number = tx.return_value
        assert number not in results
        results.append(number)
