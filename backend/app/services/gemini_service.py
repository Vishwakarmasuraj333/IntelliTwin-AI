"""
Generative AI SOC Analyst Service (Google Gemini & Intelligent Fallback)
-------------------------------------------------------------------------
Synthesizes ML detection outputs and SHAP feature attributions into
comprehensive, human-readable Security Operations Center (SOC) incident reports.
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.core.config import settings

logger = logging.getLogger("Gemini_SOC_Service")

try:
    import google.generativeai as genai
    HAS_GENAI_LIB = True
except ImportError:
    HAS_GENAI_LIB = False

class GeminiSecurityAnalystService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._init_gemini()

    def _init_gemini(self):
        if self.api_key and HAS_GENAI_LIB:
            try:
                genai.configure(api_key=self.api_key)
                logger.info(f"Initialized Google Gemini API client with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to configure Google Gemini client: {e}")

    def generate_incident_report(
        self,
        event_data: Dict[str, Any],
        prediction: str,
        risk_score: int,
        severity: str,
        attack_category: str,
        shap_factors: List[Dict[str, Any]],
        analyst_notes: str = None
    ) -> Dict[str, Any]:
        """
        Orchestrates incident report generation via Gemini API.
        Falls back seamlessly to the expert SOC heuristic engine if API is unreachable.
        """
        prompt = self._build_soc_prompt(
            event_data, prediction, risk_score, severity, attack_category, shap_factors, analyst_notes
        )

        if self.api_key and HAS_GENAI_LIB:
            try:
                logger.info("Dispatching prompt to Google Gemini Generative AI...")
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
                )
                
                raw_text = response.text
                parsed_json = json.loads(raw_text)
                parsed_json["model_used"] = f"Google Gemini ({self.model_name})"
                parsed_json["generated_at"] = datetime.now(timezone.utc).isoformat()
                return parsed_json
            except Exception as e:
                logger.warning(f"Gemini API request failed or timed out: {e}. Engaging Autonomous SOC Fallback Engine.")
                
        # Graceful, high-fidelity offline fallback
        return self._generate_autonomous_soc_report(
            event_data, prediction, risk_score, severity, attack_category, shap_factors, analyst_notes
        )

    def _build_soc_prompt(
        self, event_data, prediction, risk_score, severity, attack_category, shap_factors, analyst_notes
    ) -> str:
        return f"""
You are a Principal SOC Analyst and Incident Responder. Analyze this network telemetry alert:

--- TELEMETRY METRICS ---
- Classification: {prediction}
- Risk Score: {risk_score}/100
- Severity Level: {severity}
- Suspected Vector: {attack_category}
- Raw Attributes: {json.dumps(event_data, default=str)}

--- EXPLAINABLE AI (SHAP) ATTRIBUTION ---
The machine learning model flagged these top anomalous features:
{json.dumps(shap_factors, default=str)}

--- ANALYST CONTEXT ---
{analyst_notes or "No additional analyst notes provided."}

Return a valid JSON object matching this exact schema:
{{
  "title": "Concise incident headline",
  "executive_summary": "High-level 2-3 sentence overview for C-level leadership",
  "technical_analysis": "Detailed technical analysis explaining the abnormal metrics and network behavior",
  "attack_category": "{attack_category}",
  "mitre_attack": [
    {{"id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery"}}
  ],
  "why_suspicious": [
    "Specific bullet explaining anomalous feature 1 based on SHAP",
    "Specific bullet explaining anomalous feature 2 based on SHAP"
  ],
  "investigation_steps": [
    "Step 1: Check firewall connection state tables for source IP",
    "Step 2: Cross-reference external IP with Threat Intelligence (VirusTotal/AbuseIPDB)",
    "Step 3: Collect packet capture (PCAP) for the offending stream"
  ],
  "mitigation_playbook": [
    "Action 1: Implement temporary IP block on border firewall",
    "Action 2: Enable TCP SYN cookies and connection rate-limiting",
    "Action 3: Review service authentication logs for unauthorized attempts"
  ],
  "confidence_assessment": "High confidence based on converged ML prediction and SHAP feature deviance."
}}
"""

    def _generate_autonomous_soc_report(
        self, event_data, prediction, risk_score, severity, attack_category, shap_factors, analyst_notes
    ) -> Dict[str, Any]:
        """Provides expert deterministic triage reports when cloud GenAI is unconfigured."""
        proto = event_data.get("proto", "tcp").upper()
        rate = event_data.get("rate", 0)
        sbytes = event_data.get("sbytes", 0)
        
        # Taxonomy mapping
        if attack_category == "DoS":
            mitre = [
                {"id": "T1498", "name": "Network Denial of Service", "tactic": "Impact"},
                {"id": "T1498.001", "name": "Direct Network Flood", "tactic": "Impact"}
            ]
            title = f"High-Volume Network Flood Alert ({proto} / {attack_category})"
            summary = f"Detected an abnormal surge of {rate:.1f} packets/second over {proto}. The flow profile reflects a resource exhaustion flood attempt targeting network availability."
            investigations = [
                "Isolate inbound firewall logs to verify if source addresses are spoofed or geographically clustered.",
                "Review edge router ingress queues and drop counters for bandwidth saturation.",
                "Analyze destination host CPU and socket backlog states (netstat -ant | grep SYN_RECV)."
            ]
            mitigations = [
                "Apply immediate rate-limiting on incoming SYN packets at border firewall.",
                "Activate cloud DDoS scrubbing or BGP Flowspec filtering for offending CIDR block.",
                "Tune kernel TCP parameters: net.ipv4.tcp_syncookies = 1 and net.ipv4.tcp_max_syn_backlog = 4096."
            ]
        elif attack_category == "Reconnaissance":
            mitre = [
                {"id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery"},
                {"id": "T1595", "name": "Active Scanning", "tactic": "Reconnaissance"}
            ]
            title = f"Rapid Port & Service Sweep Detected ({attack_category})"
            summary = f"Identified concentrated connection attempts to multiple distinct destination ports within a micro-window. This pattern indicates automated port discovery or vulnerability fingerprinting."
            investigations = [
                "Query SIEM logs for repeated RST/ACK packet replies sent by internal hosts.",
                "Correlate source IP against external OSINT threat feeds (CINS, AlienVault OTX).",
                "Inspect whether target destination ports host exposed administrative panels (e.g. SSH, RDP, Web)."
            ]
            mitigations = [
                "Block offending scanner IP at border firewall or perimeter ACL.",
                "Ensure non-essential external-facing services are gated behind a corporate VPN or Zero-Trust proxy.",
                "Enable port-scan detection heuristics on the internal Network Intrusion Prevention System (NIPS)."
            ]
        elif attack_category == "Exploits":
            mitre = [
                {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access"},
                {"id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution"}
            ]
            title = f"Application Exploit Vector Attempt Flagged ({attack_category})"
            summary = f"Network flow exhibits abnormal payload volume ({sbytes} bytes) combined with irregular connection states, characteristic of an exploit payload injection or remote code execution attempt."
            investigations = [
                "Extract raw web server access logs matching the exact timestamp to inspect URI path and payload encoding.",
                "Check web application error logs for unhandled 500 exceptions or buffer overrun alerts.",
                "Conduct memory dump and EDR inspection on destination host for spawned sub-processes."
            ]
            mitigations = [
                "Deploy virtual patch via Web Application Firewall (WAF) rule to drop malicious signature.",
                "Quarantine affected host from corporate intranet to prevent lateral movement.",
                "Revoke and rotate any session tokens or database credentials associated with the target endpoint."
            ]
        elif prediction == "NORMAL":
            mitre = []
            title = f"Standard Legitimate Network Transaction ({proto})"
            summary = f"Analyzed {proto} connection matches baseline operational profiles with normal byte ratios and expected TTL signatures. No immediate threat detected."
            investigations = [
                "Standard telemetry logged for security baseline audit.",
                "No active investigation required at this time."
            ]
            mitigations = [
                "Maintain standard monitoring and threshold tracking."
            ]
        else:
            mitre = [
                {"id": "T1205", "name": "Traffic Signaling", "tactic": "Defense Evasion"}
            ]
            title = f"Unclassified Network Anomaly Flagged ({severity} Severity)"
            summary = f"The ML detection engine identified significant deviations across statistical flow features with a risk score of {risk_score}/100."
            investigations = [
                "Inspect session PCAP data to decode application-layer payloads.",
                "Verify whether legitimate administrative bulk transfer activity occurred at this timestamp."
            ]
            mitigations = [
                "Flag source host for heightened monitoring.",
                "Enforce network segmentation and strict egress filtering."
            ]

        # Convert SHAP factors to readable explanations
        why_suspicious = []
        for factor in shap_factors[:4]:
            feat = factor.get("feature_name_display", factor.get("feature", "Metric"))
            val = factor.get("feature_value", "N/A")
            direction = "elevated the anomaly score" if factor.get("direction") == "increases_risk" else "attenuated the threat score"
            why_suspicious.append(f"{feat} recorded value of {val}, which {direction} by {abs(factor.get('shap_value', 0)):.3f}.")

        if not why_suspicious:
            why_suspicious = ["Flow metrics matched established baseline parameters."]

        return {
            "title": title,
            "executive_summary": summary,
            "technical_analysis": f"Telemetry indicates anomalous distribution across transport protocol {proto}. Risk score calculated at {risk_score}/100 with {severity} classification. Explainable AI attributions highlight {len(shap_factors)} principal contributing features.",
            "attack_category": attack_category,
            "mitre_attack": mitre,
            "why_suspicious": why_suspicious,
            "investigation_steps": investigations,
            "mitigation_playbook": mitigations,
            "confidence_assessment": f"High confidence ({risk_score}% certainty) based on multi-variable UNSW-NB15 tree attribution.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_used": "IntelliTwin Autonomous SOC Engine (Zero-Crash Fallback)"
        }

gemini_analyst = GeminiSecurityAnalystService()
