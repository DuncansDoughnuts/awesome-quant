import uuid


class OrderManager:
    def __init__(self):
        self.pending = {}
        self.completed = {}

    def client_id(self, strategy_id, instrument):
        return f"{strategy_id}-{instrument}-{uuid.uuid4().hex[:12]}"

    def register(self, order):
        self.pending[order["client_order_id"]] = order

    def fill(self, client_order_id, fill):
        self.completed[client_order_id] = fill
        self.pending.pop(client_order_id, None)
