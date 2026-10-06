import os
import tempfile

import tables
from pywr.core import Model, Input, Output
from pywr.recorders import TablesRecorder

# Solve a tiny model with both linked solver backends (proves the
# glpk/lpsolve extensions work at solve time, not just at import).
for solver in ("glpk", "lpsolve"):
    m = Model(start="2020-01-01", end="2020-01-02", solver=solver)
    i = Input(m, "supply", max_flow=10)
    o = Output(m, "demand", max_flow=8, cost=-1)
    i.connect(o)
    m.run()
    assert o.flow[0] == 8, (solver, o.flow)
    print(f"{solver} solve OK: flow {o.flow[0]}")

# Exercise PyTables I/O (TablesRecorder write + read back).
m = Model(start="2020-01-01", end="2020-01-02", solver="glpk")
i = Input(m, "supply", max_flow=10)
o = Output(m, "demand", max_flow=8, cost=-1)
i.connect(o)
with tempfile.TemporaryDirectory() as td:
    h5 = os.path.join(td, "out.h5")
    TablesRecorder(m, h5)
    m.run()
    assert os.path.exists(h5)
    with tables.open_file(h5) as h5f:
        ca = h5f.get_node("/", "demand")
        assert ca.shape == (2, 1), ca.shape
        assert abs(ca[0][0] - 8) < 1e-9, ca[0][0]
print("tables I/O OK")
