class ExecutionRouter:
    def __init__(self,mapping=None): self.venues={}; self.mapping=mapping or {}
    def register(self,name,venue): self.venues[name.upper()]=venue
    def map_asset_class(self,asset_class,venue_name): self.mapping[asset_class.upper()]=venue_name.upper()
    def get(self,name):
        key=name.upper()
        if key not in self.venues: raise KeyError(f'No execution venue registered for {name}')
        return self.venues[key]
    def for_asset_class(self,asset_class,paper=False):
        if paper:return self.get('PAPER')
        name=self.mapping.get(asset_class.upper())
        if not name: raise KeyError(f'No execution mapping for asset class {asset_class}')
        return self.get(name)
