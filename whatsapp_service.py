import requests
import time
from datetime import datetime
import os

# WhatsApp Business API Configuration
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '850720011454978')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', 'EAAUpEZC6VFNkBP4CWFZAxoZATXATORyAZCPPi8LW07amVNNuqqvVJl9uxZBgFQgwRhK5v8XqJlZCV61nOfjzSHbZCd7DWBV6bKfKUiba4ju0w3WZAmJbyo1ug3goFGmoCKAD25EWWGNWCSJ1qWLX6bDyWZAm8VtHSYnhCG1GNJpksTRZC080MKhM2QETyUNS4JWfErlsnGQqsZBwOCpnK6MZAdmHg7Kof0wbqWNff05ZCFJ1BZBggZD')
WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v21.0')

# Message delay (seconds) - to avoid rate limiting
DELAY_BETWEEN_MESSAGES = 2


class WhatsAppService:
    """WhatsApp Business API Service"""
    
    def __init__(self, phone_number_id=None, access_token=None, api_version=None):
        self.phone_number_id = phone_number_id or WHATSAPP_PHONE_NUMBER_ID
        self.access_token = access_token or WHATSAPP_ACCESS_TOKEN
        self.api_version = api_version or WHATSAPP_API_VERSION
        self.api_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def send_text_message(self, to_phone, message_text):
        """
        Send a text message via WhatsApp Business API
        
        Args:
            to_phone: Phone number with country code (without +)
            message_text: Message content
        
        Returns:
            dict: API response with success status
        """
        if not self.access_token:
            return {"success": False, "error": "WhatsApp access token not configured"}
        
        # Clean phone number (remove +, spaces, dashes)
        to_phone = to_phone.replace('+', '').replace(' ', '').replace('-', '')
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": message_text
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json() if response.text else {}
                return {"success": False, "error": error_data}
            except:
                return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_bulk_messages(self, contacts, message, delay=DELAY_BETWEEN_MESSAGES):
        """
        Send bulk messages to multiple contacts
        
        Args:
            contacts: List of phone numbers (with or without +)
            message: Message text
            delay: Delay between messages in seconds
        
        Returns:
            dict: Broadcast results with success/failure counts
        """
        if not self.access_token:
            return {
                "success": False,
                "error": "WhatsApp access token not configured",
                "total": len(contacts),
                "sent": 0,
                "failed": len(contacts),
                "results": []
            }
        
        results = {
            "total": len(contacts),
            "sent": 0,
            "failed": 0,
            "results": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for idx, phone in enumerate(contacts, 1):
            # Clean phone number
            clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            # Skip if phone number is empty or invalid
            if not clean_phone or len(clean_phone) < 10:
                results["failed"] += 1
                results["results"].append({
                    "phone": phone,
                    "success": False,
                    "error": "Invalid phone number"
                })
                continue
            
            # Send message
            response = self.send_text_message(clean_phone, message)
            
            if response.get("success"):
                results["sent"] += 1
                results["results"].append({
                    "phone": phone,
                    "success": True,
                    "message_id": response.get("data", {}).get("messages", [{}])[0].get("id", "")
                })
            else:
                results["failed"] += 1
                results["results"].append({
                    "phone": phone,
                    "success": False,
                    "error": str(response.get("error", "Unknown error"))
                })
            
            # Delay between messages (except for the last one)
            if idx < len(contacts) and delay > 0:
                time.sleep(delay)
        
        return results
    
    def verify_credentials(self):
        """Verify WhatsApp API credentials"""
        if not self.access_token:
            return False
        
        try:
            # Try to get phone number info
            verify_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
            response = requests.get(verify_url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except:
            return False

