import json
import psycopg
from psycopg.rows import dict_row
class MemoryStore:
    def __init__(self,dsn): self.dsn=dsn
    def audit(self,instance_id,event_type,payload):
        sql="INSERT INTO audit_events(event_type,instance_id,payload) VALUES (%s,%s,%s::jsonb)"
        with psycopg.connect(self.dsn) as conn: conn.execute(sql,(event_type,instance_id,json.dumps(payload,default=str)))
    def remember(self,memory_type,subject,summary,evidence=None,confidence=0.5):
        sql="INSERT INTO memories(memory_type,subject,summary,evidence,confidence) VALUES (%s,%s,%s,%s::jsonb,%s)"
        with psycopg.connect(self.dsn) as conn: conn.execute(sql,(memory_type,subject,summary,json.dumps(evidence or {}),confidence))
    def recall(self,subject,limit=8):
        sql="SELECT ts,memory_type,subject,summary,evidence,confidence FROM memories WHERE subject=%s AND (expires_at IS NULL OR expires_at>now()) ORDER BY ts DESC LIMIT %s"
        with psycopg.connect(self.dsn,row_factory=dict_row) as conn: return list(conn.execute(sql,(subject,limit)).fetchall())
