import tables as tb

FILTERS = tb.Filters(complib='blosc', complevel=9)
h5file = tb.open_file("../data/market.hdf5", mode="a", title="Market Data Collection",
                      filters=FILTERS)

