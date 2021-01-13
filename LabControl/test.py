"""
    def mini(self):
        x0 = np.array([0, 0])
        def fun(x):
            I, Q = x
            self.qm.set_dc_offset_by_qe("qubit", "I", float(I))
            self.qm.set_dc_offset_by_qe("qubit", "Q", float(Q))
            _, amps = self.sa124B.initSweepSingle(center=self.carrier, power=self.power)
        minimize(fun, x0, bounds=None)
    """   