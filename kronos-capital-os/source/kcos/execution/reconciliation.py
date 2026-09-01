class Reconciler:
    def compare_positions(self,internal,external,tolerance=1e-8):
        a={(p.venue,p.instrument):p.qty for p in internal}; b={(p.venue,p.instrument):p.qty for p in external}; keys=set(a)|set(b); diffs=[]
        for k in keys:
            if abs(a.get(k,0)-b.get(k,0))>tolerance: diffs.append({'key':k,'internal':a.get(k,0),'external':b.get(k,0)})
        return {'ok':not diffs,'differences':diffs}
