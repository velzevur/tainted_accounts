import requests
import pprint
from datetime import datetime

mdw = 'http://mdw.mainnet.aeternity.io/mdw'
exchanges = {\
'ak_vKdT14HCiLCxuT3M7vf3QREyUbQTr1u6Pz49ba9EhaD6uDqWs': 'Huobi',\
'ak_Jzo4GUqW67gZiA9Cenjxd87h5L2KYvJncDpcnTWbEPUUxZaXn': 'Huobi',\
'ak_2tNbVhpU6Bo3xGBJYATnqc62uXjR8yBv9e63TeYCpa6ASgEz94': 'gate.io',\
'ak_6sssiKcg7AywyJkfSdHz52RbDUq5cZe4V4hcvghXnrPz4H4Qg': 'gate.io',\
'ak_dnzaNnchT7f3YT3CtrQ7GUjqGT6VaHzPxpf2efHWPuEAWKcht': 'Binance',\
'ak_2kGjej4M4YCPpK6yxhaTP6Kyxejd6w22wdMcUQkhNRuZy2JchH': 'Bithumb',\
'ak_3jgongnfUibKiXBUVCtwXMWbM8hzifRm6C1E4Fp3mKbAT7ZQ9': 'Bithumb',\
'ak_Tmwf23kcVVXvJwb79G68wBtyEL9iTSGQRzZz4DJxwTxJWbM1': 'Bithumb',\
'ak_6HzvyAruY8Wehw5amSNULMX2DD4nGikJ31HmKksYNkWms8EVR': 'ZB.com',\
'ak_2mggc8gkx9nhkciBtYbq39T6Jzd7WBms6jgYoLAAeRNgdy3Md6': 'ZB.com',\
'ak_FekquK8dzWypxLCmUe8SJBKYhXUF13umHi9W3EDMrycdEn3t4': 'ZB.com',\
'ak_3oCNr4upswn5sRVpqdpuiCwxqwRU1tok2xLjLLy9vjvYRdVNd': 'CoinEX',\
'ak_2jAKqpercZZhfJ397yBuWfxZXfdCUGSkDiJuNtokNeeDV1Y13q': 'BigONE',\
'ak_N1a9HyfqpbvWV5vGejWMduf4yn8yeiXNz6AzU22iwGDT35NXh': 'Coinw',\
'ak_2BiHjeyudimaRgjf7yYtD3ptbKhUfAV7K4wrTBKLT13oRLosnS': 'uex',\
'ak_2dKH7FpWYVg8kvBtK9WpQDspZPgBuRNrNhEMmMp6Qp4ogdGQiX': 'StealthEx',\
'ak_2Q4St96FUCR2GrhYctpy11xVNk99epahpB6NH4XxpY1UxmYkQg': 'QBTC',\
'ak_4vMR6bPdfQyKme4XKLCetRAJePNBKi3q33CUk8q4tPzM2onSU': 'OKEX',\
'ak_CnHJnqaNK8zjy3my6DWWXXWKTQoMPvmSwBzxfeenw5YFYekwR': 'AEX',\
'ak_jgiBUko9fTwg5HQ8nHFoPbjR22TBcg9LK85qsv1mTkcjdszFa': 'MXC',\
'ak_hmtayWUNHXdyhk96Yw7VzsdDmdp4AWcjemzEvs7fZg8imipTz': 'CEOExchange',\
'ak_wftXwsMheVNA33YWiYLqFNnSSDnYsV9ynqRSnZT8P3kgZG9bn': 'Hotbit.io',\
'ak_2dgpHzehWzMPUCubSuUhSef1QRbZ12PvBZGLuh7gWWZHvG3ukh': 'decoy'}
all_tainted_accounts = set(exchanges.keys())
transfers = {}
transactions = {}
aetto = 10**18
visited = set()

def txs_from_account(account):
  response = requests.get(mdw + '/txs/forward?spend.sender_id=' + account).json()
  res = response['data']
  next_p = response['next']
  while next_p:
    print('Fetching ' + next_p)
    nresponse = requests.get(mdw + next_p).json()
    next_p = nresponse['next']
    res = res + nresponse['data']
  return res

def trace(account):
  return trace_(account, 1)

def trace_(account, ident):
  print(' ### ' + name(account))
  txs = txs_from_account(account)
  for w in txs:
    tx_hash = w['hash']
    if tx_hash in transactions:
      ##print(account + 'is already processed')
      pass
    else:
      print('Processing ' + tx_hash)
      transactions[tx_hash] = w
      tx = w['tx']
      sender = tx['sender_id']
      recipient = tx['recipient_id']
      all_tr = transfers.get(sender, {})
      r_tr = all_tr.get(recipient, [])
      r_tr.append(tx_hash)
      all_tr[recipient] = r_tr
      transfers[sender] = all_tr
      if recipient in all_tainted_accounts:
        pass
      else:
        trace_(recipient, ident + 1)

def name(account):
  nick = exchanges.get(account)
  if nick:
    return account + ' (' + nick + ')'
  else:
    return account

def print_(account):
  visited = set()
  print(account)
  print__(account, 1)

def print__(account, ident):
  visited.add(account)
  for r, tx_hashes in transfers.get(account, {}).items():
      if r in visited:
        print(ident * '    ' + '|-> ' + name(r) + ' ' + str(len(tx_hashes)) + ' txs')
        pass
      else:
        sum = 0
        f = lambda s, x: s + x['tx']['amount']
        [sum := f(sum, transactions[h]) for h in tx_hashes]
        print(ident * '    ' + '|-> ' + name(r) + ' ' + str(len(tx_hashes)) + ' txs, with total amount of ' + str(sum/aetto) + 'AE')
        print__(r, ident + 1)

addr = 'ak_2VgB6KRVkpG1UwHcZufnhcFKMEwVJwBc75U6VWKko8c5GrbU1i'
all_tainted_accounts.add(addr)

trace(addr)
pp = pprint.PrettyPrinter(indent=2)
##pp.pprint(transfers)
print_(addr)
