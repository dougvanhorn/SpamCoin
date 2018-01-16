#!/usr/bin/env python3
"""Simple BlockChain implementation.

Links:

    https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b
    https://en.bitcoin.it/wiki/Protocol_documentation
"""

import datetime
import hashlib
import time

import click


# Global log level, modulate via command line argument.
VERBOSE = False


class Block:
    """A very simple block.

    In crypto-currency a block would contain a coinbase record, giving the miner one coin.  This
    serves as incentive to mine, and to make each hashing pool's work unique to them.
    """
    def __init__(self, height, timestamp, data, previous_hash, nonce):
        """Construct a block.

        Arguments:
            height: where this block is at in the chain
            timestamp: when this block was created
            data: the data to be stored in the block
            previous_hash: a pointer to the previous block's hash
            nonce: [None] A nonce to alter the hash of this block
        """
        self.height = height
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.hash_block()

    def __str__(self):
        return '{}'.format(self.hash)

    def hash_block(self):
        """Build the sha256 string for the block.

        The block's hash is based on the it's contents.

        Returns:
            A hexdigest of a sha256 hash.
        """
        sha = hashlib.sha256()
        sha.update(str(self.height).encode('utf-8'))
        sha.update(self.timestamp.isoformat().encode('utf-8'))
        sha.update(str(self.data).encode('utf-8'))
        sha.update(str(self.previous_hash).encode('utf-8'))
        sha.update(str(self.nonce).encode('utf-8'))

        return sha.hexdigest()


def create_genesis_block():
    """Create first block, height 0 previous hash 0.

    Returns:
        A Block instance.
    """
    return Block(0, datetime.datetime.now(), 'Let there be coin.', '0', nonce=0)


def mine_next_block(last_block, difficulty=None):
    """Generate and return the next block in the chain.

    Arguments:
        last_block: the last block in the chain to point to
        difficulty: [int] the difficulty, number of zeros the hash much start with

    Returns:
        A new Block to be appended to the chain.
    """
    height = last_block.height + 1
    timestamp = datetime.datetime.now()
    data = 'This is where the block transactions would go.  Height: %s.' % height

    rounds = 0
    block = Block(height, timestamp, data, last_block.hash, nonce=rounds)

    if not difficulty:
        return block

    # This is a simple difficulty check, where the new hash must begin with the specified number of
    # zeros.  Bitcoin requires the zeros plus the hash must be less than the previous block's hash
    # number.
    while not block.hash.startswith('0'*difficulty):  # noqa: E226
        rounds += 1
        block = Block(height, timestamp, data, last_block.hash, nonce=rounds)
        if (rounds % 100) == 0:
            verbose('%s rounds' % rounds)

    return block


def demo(height=20, difficulty=None):
    """Start a blockchain.

    Arguments:
        height: [20] the number of blocks to generate
        difficulty: [None] the number of 0s required at the beginning of the hash
    """
    genesis_block = create_genesis_block()
    chain = [genesis_block]

    start = time.time()
    for i in range(height - 1):  # Genesis block counts as one.
        new_block = mine_next_block(chain[-1], difficulty=difficulty)
        chain.append(new_block)

        out('A Block has been added to the blockchain.')
        out('%s: %s rounds' % (str(new_block), new_block.nonce))

    end = time.time()

    avg_rounds = sum(block.nonce for block in chain) / len(chain)

    out('Created a blockchain with a height of %s.' % len(chain))
    out('Execution time: %ss' % str(round((end - start), 2)))
    out('Average number of rounds: %s' % str(round(avg_rounds)))


def out(s):
    click.secho(s)


def verbose(s):
    if VERBOSE:
        click.secho(s, fg='green')


@click.command()
@click.option('--height', default=20, help='Number of blocks in the chain.', type=int)
@click.option('--difficulty', default=None, help='Hashing difficulty.', type=int)
@click.option('--verbose', '-v', is_flag=True, default=False, help='Be verbose about it.')
def cli(height, difficulty, verbose):
    global VERBOSE
    VERBOSE = verbose
    demo(height=height, difficulty=difficulty)


if __name__ == '__main__':
    cli()

