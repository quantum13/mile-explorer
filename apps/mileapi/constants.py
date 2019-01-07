TransferAssetsTransaction = 1
UnregisterNodeTransaction = 2
RegisterNodeTransactionWithAmount = 3
CreateTokenRateVoting = 4
PostTokenRate = 5
GetTokenRate = 6
EmissionTransaction = 7
UpdateEmission = 8

ProducerEmission = 65534
ProducerFee = 65533

TX_TYPES = {
    'TransferAssetsTransaction': TransferAssetsTransaction,
    'UnregisterNodeTransaction': UnregisterNodeTransaction,
    'RegisterNodeTransactionWithAmount': RegisterNodeTransactionWithAmount,
    'CreateTokenRateVoting': CreateTokenRateVoting,
    'PostTokenRate': PostTokenRate,
    'GetTokenRate': GetTokenRate,
    'EmissionTransaction': EmissionTransaction,
    'UpdateEmission': UpdateEmission,
    'ProducerEmission': ProducerEmission,
    'ProducerFee': ProducerFee
}

TX_TYPES_HUMAN = {
    TransferAssetsTransaction: 'transfer',
    UnregisterNodeTransaction: 'unregister node',
    RegisterNodeTransactionWithAmount: 'register node',
    CreateTokenRateVoting: 'create rate voting',
    PostTokenRate: 'post rate',
    GetTokenRate: 'get rate',
    EmissionTransaction: 'emission',
    UpdateEmission: 'update emission',
    ProducerEmission: 'producer emission',
    ProducerFee: 'producer fee'
}