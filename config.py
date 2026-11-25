"""
Configuration file for Privacy-Preserving Intelligent Cyber Threat Detection.
"""
import os

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

TRAIN_CSV = os.path.join(RAW_DIR, "train", "train.csv")
TEST_CSV = os.path.join(RAW_DIR, "test", "test.csv")
VALIDATION_CSV = os.path.join(RAW_DIR, "validation", "validation.csv")

# ─── Dataset Columns ────────────────────────────────────────────────────────
LABEL_COLUMN = "label"

FEATURE_COLUMNS = [
    "flow_duration", "Header_Length", "Protocol Type", "Duration",
    "Rate", "Srate", "Drate",
    "fin_flag_number", "syn_flag_number", "rst_flag_number",
    "psh_flag_number", "ack_flag_number", "ece_flag_number", "cwr_flag_number",
    "ack_count", "syn_count", "fin_count", "urg_count", "rst_count",
    "HTTP", "HTTPS", "DNS", "Telnet", "SMTP", "SSH", "IRC",
    "TCP", "UDP", "DHCP", "ARP", "ICMP", "IPv", "LLC",
    "Tot sum", "Min", "Max", "AVG", "Std", "Tot size",
    "IAT", "Number", "Magnitue", "Radius", "Covariance", "Variance", "Weight",
]

# Top features selected via importance analysis (reduces memory & training time)
SELECTED_FEATURES = [
    "Header_Length", "Rate", "Srate", "Drate",
    "fin_flag_number", "syn_flag_number", "rst_flag_number",
    "psh_flag_number", "ack_flag_number",
    "ack_count", "syn_count", "fin_count", "rst_count",
    "HTTP", "HTTPS", "DNS", "TCP", "UDP",
    "Tot sum", "Min", "Max", "AVG", "Std", "Tot size",
    "IAT", "Number", "Magnitue", "Radius", "Covariance", "Variance", "Weight",
]

# ─── Attack Category Mapping ────────────────────────────────────────────────
ATTACK_CATEGORIES = {
    "BenignTraffic": "Benign",
    "DDoS-ICMP_Flood": "DDoS",
    "DDoS-UDP_Flood": "DDoS",
    "DDoS-TCP_Flood": "DDoS",
    "DDoS-PSHACK_Flood": "DDoS",
    "DDoS-SYN_Flood": "DDoS",
    "DDoS-RSTFINFlood": "DDoS",
    "DDoS-SynonymousIP_Flood": "DDoS",
    "DDoS-ICMP_Fragmentation": "DDoS",
    "DDoS-UDP_Fragmentation": "DDoS",
    "DDoS-ACK_Fragmentation": "DDoS",
    "DDoS-HTTP_Flood": "DDoS",
    "DDoS-SlowLoris": "DDoS",
    "DoS-UDP_Flood": "DoS",
    "DoS-TCP_Flood": "DoS",
    "DoS-SYN_Flood": "DoS",
    "DoS-HTTP_Flood": "DoS",
    "Mirai-greeth_flood": "Mirai",
    "Mirai-udpplain": "Mirai",
    "Mirai-greip_flood": "Mirai",
    "Recon-HostDiscovery": "Reconnaissance",
    "Recon-OSScan": "Reconnaissance",
    "Recon-PortScan": "Reconnaissance",
    "Recon-PingSweep": "Reconnaissance",
    "MITM-ArpSpoofing": "Spoofing",
    "DNS_Spoofing": "Spoofing",
    "VulnerabilityScan": "Reconnaissance",
    "DictionaryBruteForce": "BruteForce",
    "BrowserHijacking": "WebAttack",
    "CommandInjection": "WebAttack",
    "SqlInjection": "WebAttack",
    "XSS": "WebAttack",
    "Backdoor_Malware": "Malware",
    "Uploading_Attack": "WebAttack",
}

CATEGORY_SEVERITY = {
    "Benign": "None",
    "DDoS": "Critical",
    "DoS": "High",
    "Mirai": "Critical",
    "Reconnaissance": "Medium",
    "Spoofing": "High",
    "BruteForce": "High",
    "WebAttack": "High",
    "Malware": "Critical",
}

# ─── Training Parameters ────────────────────────────────────────────────────
CHUNK_SIZE = 50000          # rows per chunk for memory-efficient loading
SAMPLE_SIZE = 200000        # max rows for training (RAM-safe on 8 GB)
TEST_SAMPLE_SIZE = 50000    # max rows for evaluation
RANDOM_STATE = 42

# Random Forest parameters (tuned for speed + accuracy)
RF_PARAMS = {
    "n_estimators": 100,
    "max_depth": 20,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "n_jobs": -1,
    "random_state": RANDOM_STATE,
    "class_weight": "balanced",
}

# XGBoost parameters
XGB_PARAMS = {
    "n_estimators": 100,
    "max_depth": 10,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
    "tree_method": "hist",         # fastest on CPU
    "eval_metric": "mlogloss",
}

# Isolation Forest parameters
ISO_FOREST_PARAMS = {
    "n_estimators": 100,
    "contamination": 0.1,
    "max_samples": "auto",
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
}

# ─── Federated Learning ─────────────────────────────────────────────────────
FL_NUM_CLIENTS = 3
FL_NUM_ROUNDS = 5
FL_LOCAL_EPOCHS = 1
FL_BATCH_SIZE = 64

# ─── Dashboard ───────────────────────────────────────────────────────────────
STREAMLIT_PAGE_TITLE = "CyberShield AI — IoT Threat Detection"
STREAMLIT_PAGE_ICON = "🛡️"
STREAMLIT_LAYOUT = "wide"
