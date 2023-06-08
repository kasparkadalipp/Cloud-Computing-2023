import os
import redis
import time
import decimal
import math
from flask import Flask, render_template, request  # https://flask.palletsprojects.com/en/1.1.x/api/#flask.request

app = Flask(__name__)
cache = redis.Redis(host='0.0.0.0', port=6379, decode_responses=True)

def compute_pi(n):
  """
  This function calculates the value of pi to 'n' number of decimal places
  Args:
  n:   precision(Decimal places)
  Returns:
  pi:   the value of pi to n-decimal places
  """
  
  decimal.getcontext().prec = n + 3
  decimal.getcontext().Emax = 999999999
  
  C = 426880 * decimal.Decimal(10005).sqrt()
  K = decimal.Decimal(6)
  M = decimal.Decimal(1)
  X = decimal.Decimal(1)
  L = decimal.Decimal(13591409)
  S = L
  
  # For better precision, we calculate to n+3 and truncate the last two digits
  for i in range(1, n+3):
    M = decimal.Decimal(M* ((1728*i*i*i)-(2592*i*i)+(1104*i)-120)/(i*i*i))
    L = decimal.Decimal(545140134+L)
    X = decimal.Decimal(-262537412640768000*X)
    S += decimal.Decimal((M*L) / X)
    
  return str(C/S)[:-2] # Pi is C/S

@app.route('/')
def home():

    # First, gather some data about the request (requester's address, whether there is a FORWARD header) and this server
    remote_addr = request.environ['REMOTE_ADDR']

    forwarded_for = request.environ.get('HTTP_X_FORWARDED_FOR', None)  # 2nd argument is default value if the header is not found

    # this host's IP address (note that interface ens3 may not work on different hosts/networks outside of this lab)
    server_addr = os.popen('ip addr show ens3').read().split("inet ")[1].split("/")[0]

    # Second, increase the request counters stored in Redis Cache:
    # If request is coming from a load balancer, increment the original user IP as well:
    if forwarded_for is not None:
        cache.hincrby('addresses', forwarded_for, 1) # update hashmap "addresses" by incrementing the key "forwarded_for" by value of 1
    # Increment the direct request location IP:
    cache.hincrby('addresses', remote_addr, 1)

    # Finally, check if request was made through a load balancer
    addresses = []

    # iterate over keys, values stored in redis hashmap with id "addresses":
    for (ip, hits) in cache.hgetall('addresses').items():
        address = {'ip': ip, 'hits': hits }
        if forwarded_for == ip:
            address['message'] = "* Your 'real' location"
            address['html_class'] = "address real-location"
        elif forwarded_for and remote_addr == ip:
            address['message'] = "* Connected through LB "
            address['html_class'] = "address through-lb"
        elif remote_addr == ip:
            address['message'] = "* You're directly connected, no LB"
            address['html_class'] = "address direct"
        else:
            address['message'] = ""
            address['html_class'] = "address"
        addresses.append(address)

    pi = compute_pi(n=1000)

    # pass the data to Jinja template
    return render_template('index.html',server_addr=server_addr, remote_addr=remote_addr, addresses=addresses, pi=pi)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)