def prime_factors(n):
    d = 2
    while n > 1:
        if n%d:
            d += 1+(d&1)
        else:
            n //= d
            yield d
        if d*d>n:
            yield n
            break
def spread_factors(factors,comp=lambda x,y: x*x > y):
    x = y = 1
    for f in factors:
        if comp(x,y):
            y *= f
        else:
            x *= f
    return x,y
def timer_args_pair(period,m=512,maxs=1<<16,maxp=1<<32):
    #computes pair of prescaler,period values where
    # the faster one has period closest to period
    # the slower one has period exactly m times the faster one
    # x,y,z,w <= maxv and xy ~ period, and zw = mxy
    # so xy <= (maxv**2)/m
    if period*m > maxp*maxs:
        period = maxp*maxs/m
    goalp = round(period)
    other = goalp+2*(goalp<period)-1
    while 1:
        smol = [i for i in prime_factors(goalp)][::-1]
        big = [i for i in prime_factors(m)]+smol
        big.sort(reverse=True)
        x,y = spread_factors(smol)
        z,w = spread_factors(big)
        if z > maxs or w > maxp:#try again
            goalp,other = other,goalp
            other += 2*(other>goalp)-1
            continue
        return x,y,z,w
