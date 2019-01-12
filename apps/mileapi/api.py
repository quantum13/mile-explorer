from apps.mileapi.rpc import Rpc


async def get_current_block():
    rpc = Rpc('get-current-block-id', params={})
    res, _ = await rpc.exec()
    return int(res['current-block-id'])


async def get_block(block_id):
    rpc = Rpc('get-block', params={"block-id": block_id})
    res, _ = await rpc.exec()
    return res['block-data']


async def get_wallet(pub_key):
    rpc = Rpc('get-wallet-state', params={"public-key": pub_key})
    res, _ = await rpc.exec()
    return res


async def get_wallet_after_block(pub_key, block_id):
    block, url = await Rpc('get-block', params={"block-id": block_id}).exec()
    wallet, _ = await Rpc('get-wallet-state', params={"public-key": pub_key}).exec(url)
    return wallet
