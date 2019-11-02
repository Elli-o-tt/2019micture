import ipfshttpclient
from flask import Flask, flash, render_template

def mov(address):
   return render_template(address)

if __name__ == '__main__':
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
    res = client.add(r'C:\Users\sehoon\Desktop\tes.png')
    lst=list(res.values())

    #client.get("QmcwXtDZ54ykVKp4f3nEVLKk1aHEoHH7HTb8BLBYi4qzU7")

    add='localhost:8080/ipfs/'+lst[1]
    mov(add)

