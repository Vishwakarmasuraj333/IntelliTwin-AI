"""
Network Detection Simulator & Inference Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class NetworkPacketInput(BaseModel):
    # Core attributes requested by user:
    # protocol, packet size, duration, source bytes, destination bytes, connection count
    proto: str = Field(default="tcp", description="Protocol: tcp, udp, arp, icmp, ospf")
    dur: float = Field(default=0.15, ge=0.0, le=3600.0, description="Duration of connection in seconds")
    sbytes: int = Field(default=1200, ge=0, description="Source to destination transaction bytes")
    dbytes: int = Field(default=3500, ge=0, description="Destination to source transaction bytes")
    spkts: int = Field(default=15, ge=1, description="Source to destination packet count")
    dpkts: int = Field(default=18, ge=0, description="Destination to source packet count")
    service: str = Field(default="http", description="Service: http, dns, ftp, ssh, smtp, pop3, -")
    state: str = Field(default="FIN", description="Connection state: FIN, CON, INT, REQ, RST")
    ct_srv_src: int = Field(default=2, ge=1, description="Connections to same service and source IP")
    ct_dst_ltm: int = Field(default=2, ge=1, description="Connections to same destination IP in last 100")
    ct_src_dport_ltm: int = Field(default=1, ge=1, description="Connections to same destination port")
    ct_dst_sport_ltm: int = Field(default=1, ge=1, description="Connections to same source port")
    ct_dst_src_ltm: int = Field(default=1, ge=1, description="Connections to same source & destination IP")
    sttl: int = Field(default=64, ge=0, le=255, description="Source time-to-live")
    dttl: int = Field(default=60, ge=0, le=255, description="Destination time-to-live")
    sloss: int = Field(default=0, ge=0, description="Source packets lost")
    dloss: int = Field(default=0, ge=0, description="Destination packets lost")

class ShapFeature(BaseModel):
    feature: str
    feature_name_display: str
    shap_value: float
    feature_value: Any
    direction: str # 'increases_risk' or 'decreases_risk'

class PredictionResponse(BaseModel):
    event_id: str
    prediction: str # 'NORMAL' or 'ANOMALY'
    confidence: float # 0.0 to 1.0
    risk_score: int # 0 to 100
    severity: str # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    attack_category: str # 'Normal', 'DoS', 'Exploits', 'Fuzzers', etc.
    model_name: str
    model_version: str
    shap_values: List[ShapFeature]
    analyzed_at: datetime
    input_features: Dict[str, Any]
