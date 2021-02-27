


def graph(func,x=range(100)):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(nrows=1, ncols=1)
    x = [i for i in x]
    ax.plot(x,[func(i) for i in x])
    plt.show(block=0)
