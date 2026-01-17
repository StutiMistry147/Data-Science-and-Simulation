from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
from collections import defaultdict
import threading
import pandas as pd

class RuleEngine:
    def __init__(self):
        self.rules = {
            'large_amount': {
                'threshold': 5000,
                'enabled': True,
                'description': 'Transactions above $5000'
            },
            'rapid_transactions': {
                'threshold': 3,  # transactions
                'time_window': 300,  # seconds
                'enabled': True,
                'description': '3+ transactions in 5 minutes'
            },
            'odd_hours': {
                'start_hour': 23,  # 11 PM
                'end_hour': 6,     # 6 AM
                'enabled': True,
                'description': 'Transactions between 11 PM and 6 AM'
            },
            'geographic_impossible': {
                'max_speed_kmh': 800,
                'enabled': True,
                'description': 'Impossible geographic travel'
            },
            'suspicious_countries': {
                'countries': {'RU', 'NG', 'UA', 'KP', 'SY'},
                'enabled': True,
                'description': 'Transactions from high-risk countries'
            },
            'unusual_merchant': {
                'suspicious_merchants': {'DARK_WEB_STORE', 'UNKNOWN_VENDOR', 'TEST_MERCHANT'},
                'enabled': True,
                'description': 'Transactions with suspicious merchants'
            }
        }
        
        self.transaction_history = defaultdict(list)
        self.lock = threading.Lock()
        
        self.country_coords = {
            'US': (37.0902, -95.7129),
            'UK': (55.3781, -3.4360),
            'CA': (56.1304, -106.3468),
            'AU': (-25.2744, 133.7751),
            'DE': (51.1657, 10.4515),
            'FR': (46.2276, 2.2137),
            'JP': (36.2048, 138.2529),
            'SG': (1.3521, 103.8198),
            'IN': (20.5937, 78.9629),
            'RU': (61.5240, 105.3188),
            'NG': (9.0820, 8.6753),
            'UA': (48.3794, 31.1656),
            'BR': (-14.2350, -51.9253),
            'CN': (35.8617, 104.1954)
        }
    
    def _parse_timestamp(self, timestamp):
        """Parse timestamp from various formats (str, Timestamp, datetime)"""
        if isinstance(timestamp, str):
            return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        elif isinstance(timestamp, pd.Timestamp):
            return timestamp.to_pydatetime()
        elif isinstance(timestamp, datetime):
            return timestamp
        else:
            try:
                return pd.to_datetime(timestamp).to_pydatetime()
            except:
                return datetime.now()
    
    def check_large_amount(self, transaction: Dict[str, Any]) -> tuple:
        """Check if transaction amount is unusually large"""
        threshold = self.rules['large_amount']['threshold']
        if transaction['amount'] > threshold:
            return True, f"Large amount: ${transaction['amount']} > ${threshold}"
        return False, ""
    
    def check_rapid_transactions(self, transaction: Dict[str, Any]) -> tuple:
        """Check for rapid consecutive transactions"""
        with self.lock:
            account = transaction['account_id']
            timestamp = self._parse_timestamp(transaction['timestamp'])

            window_seconds = self.rules['rapid_transactions']['time_window']
            cutoff = timestamp - timedelta(seconds=window_seconds)
            self.transaction_history[account] = [
                t for t in self.transaction_history[account]
                if t[0] > cutoff
            ]

            self.transaction_history[account].append((timestamp, transaction['amount']))

            threshold = self.rules['rapid_transactions']['threshold']
            if len(self.transaction_history[account]) >= threshold:
                return True, f"Rapid transactions: {len(self.transaction_history[account])} in {window_seconds} seconds"
            
            return False, ""
    
    def check_odd_hours(self, transaction: Dict[str, Any]) -> tuple:
        """Check if transaction occurred during odd hours"""
        timestamp = self._parse_timestamp(transaction['timestamp'])
        hour = timestamp.hour
        
        start = self.rules['odd_hours']['start_hour']
        end = self.rules['odd_hours']['end_hour']
        
        if start <= 23 and hour >= start:
            return True, f"Odd hour transaction: {hour:02d}:00"
        elif end >= 0 and hour <= end:
            return True, f"Odd hour transaction: {hour:02d}:00"
        
        return False, ""
    
    def check_geographic_impossible(self, transaction: Dict[str, Any], 
                                   previous_transaction: Dict[str, Any] = None) -> tuple:
        """Check for impossible geographic travel"""
        if not previous_transaction:
            return False, ""

        current_country = transaction['country']
        previous_country = previous_transaction['country']
        
        if current_country not in self.country_coords or previous_country not in self.country_coords:
            return False, ""

        current_time = self._parse_timestamp(transaction['timestamp'])
        previous_time = self._parse_timestamp(previous_transaction['timestamp'])
        time_diff_hours = abs((current_time - previous_time).total_seconds() / 3600)
        
        if time_diff_hours == 0:
            return False, ""

        lat1, lon1 = self.country_coords[previous_country]
        lat2, lon2 = self.country_coords[current_country]

        distance_km = self._haversine_distance(lat1, lon1, lat2, lon2)

        speed_kmh = distance_km / time_diff_hours
        max_speed = self.rules['geographic_impossible']['max_speed_kmh']
        
        if speed_kmh > max_speed:
            return True, f"Impossible travel: {speed_kmh:.0f} km/h required"
        
        return False, ""
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def check_suspicious_country(self, transaction: Dict[str, Any]) -> tuple:
        """Check if transaction is from a high-risk country"""
        country = transaction['country']
        if country in self.rules['suspicious_countries']['countries']:
            return True, f"Suspicious country: {country}"
        return False, ""
    
    def check_unusual_merchant(self, transaction: Dict[str, Any]) -> tuple:
        """Check for transactions with suspicious merchants"""
        merchant = transaction.get('merchant', '')
        if merchant in self.rules['unusual_merchant']['suspicious_merchants']:
            return True, f"Suspicious merchant: {merchant}"
        return False, ""
    
    def evaluate_transaction(self, transaction: Dict[str, Any], 
                           previous_transaction: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate transaction against all rules"""
        anomalies = []
        triggered_rules = []

        for rule_name, rule_config in self.rules.items():
            if not rule_config['enabled']:
                continue
            
            is_anomalous = False
            reason = ""
            
            if rule_name == 'large_amount':
                is_anomalous, reason = self.check_large_amount(transaction)
            elif rule_name == 'rapid_transactions':
                is_anomalous, reason = self.check_rapid_transactions(transaction)
            elif rule_name == 'odd_hours':
                is_anomalous, reason = self.check_odd_hours(transaction)
            elif rule_name == 'geographic_impossible':
                is_anomalous, reason = self.check_geographic_impossible(
                    transaction, previous_transaction
                )
            elif rule_name == 'suspicious_countries':
                is_anomalous, reason = self.check_suspicious_country(transaction)
            elif rule_name == 'unusual_merchant':
                is_anomalous, reason = self.check_unusual_merchant(transaction)
            
            if is_anomalous:
                anomalies.append({
                    'rule': rule_name,
                    'description': rule_config['description'],
                    'reason': reason,
                    'severity': self._calculate_severity(rule_name, transaction)
                })
                triggered_rules.append(rule_name)
        
        return {
            'transaction_id': transaction['transaction_id'],
            'timestamp': str(transaction['timestamp']),
            'account_id': transaction['account_id'],
            'amount': transaction['amount'],
            'is_anomalous': len(anomalies) > 0,
            'anomaly_count': len(anomalies),
            'anomalies': anomalies,
            'triggered_rules': triggered_rules,
            'risk_score': self._calculate_risk_score(anomalies)
        }
    
    def _calculate_severity(self, rule_name: str, transaction: Dict[str, Any]) -> str:
        """Calculate severity of anomaly"""
        if rule_name == 'large_amount':
            amount = transaction['amount']
            if amount > 20000:
                return 'CRITICAL'
            elif amount > 10000:
                return 'HIGH'
            else:
                return 'MEDIUM'
        
        elif rule_name == 'suspicious_countries':
            return 'HIGH'
        
        elif rule_name == 'unusual_merchant':
            return 'CRITICAL'
        
        elif rule_name == 'geographic_impossible':
            return 'HIGH'
        
        else:
            return 'MEDIUM'
    
    def _calculate_risk_score(self, anomalies: List[Dict]) -> float:
        """Calculate overall risk score (0-100)"""
        severity_weights = {
            'CRITICAL': 1.0,
            'HIGH': 0.7,
            'MEDIUM': 0.4,
            'LOW': 0.2
        }
        
        if not anomalies:
            return 0.0
        
        total_score = 0
        for anomaly in anomalies:
            severity = anomaly['severity']
            total_score += severity_weights.get(severity, 0.5) * 25

        return min(total_score, 100)
    
    def update_rule(self, rule_name: str, **kwargs):
        """Update rule configuration"""
        if rule_name in self.rules:
            self.rules[rule_name].update(kwargs)
            print(f"Updated rule: {rule_name}")
        else:
            print(f"Rule not found: {rule_name}")
    
    def get_rules_status(self):
        """Get current rules configuration"""
        return self.rules
