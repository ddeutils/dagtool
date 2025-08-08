from dukdig import DokDag

dag = DokDag(name="store", path=__file__, gb=globals())
dag.gen()
