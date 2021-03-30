
# SET OF FUNCTION USED DURING PREPROCESSING

def setTCP(x):
    if x == "tcp":
        return 1
    return 0


def setUDP(x):
    if x == "udp":
        return 1
    return 0


def setICMP(x):
    if x == "icmp":
        return 1
    return 0


def setGRE(x):
    if x == "gre":
        return 1
    return 0


def setOTHER(x):
    if (x != "tcp") and (x != "udp") and (x != "icmp") and (x != "gre"):
        return 1
    return 0

def setWellKnownPort(x):
    if x < 1024:
        return 1
    return 0


def setNS(x):
    if (x & 256)!=0:
        return 1
    return 0

def setCWR(x):
    if (x & 128)!=0:
        return 1
    return 0

def setECE(x):
    if (x & 64)!=0:
        return 1
    return 0

def setURG(x):
    if (x & 32)!=0:
        return 1
    return 0

def setACK(x):
    if (x & 16)!=0:
        return 1
    return 0

def setPSH(x):
    if (x & 8)!=0:
        return 1
    return 0

def setRST(x):
    if (x & 4)!=0:
        return 1
    return 0

def setSYN(x):
    if (x & 2)!=0:
        return 1
    return 0

def setFIN(x):
    if (x & 1)!=0:
        return 1
    return 0