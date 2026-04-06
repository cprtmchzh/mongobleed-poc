from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['testdb']
userInfo = db['userInfo']
userToken = db['token']
apiKey = db['apiKey']

# admin 권한 유저 데이터 생성
adminData = {
    "username": "admin",
    "phone": "010-0000-0000",
    "password": "$2b$10$dummyhash_admin",
    "role": "admin"
}

# 일반 유저 데이터 50개 생성
userData = [
    {
        "username": f"user_{i}",
        "phone": f"010-0000-{1000 + i}",
        "password": f"$2b$10$dummyhash_{i}",
        "role": "user"
    }
    for i in range(50)
]

# 접속 유저 token 데이터 생성
token = [
    {
        "username": "admin",
        "token": "jwtToken_xxxxxxxxxxx_admin"
    }
] + [
    {
        "username": f"user_{i}",
        "token": f"jwtToken_xxxxxxxxxxx_{i}"
    }
    for i in range(10)
]

# apiKey 데이터 생성
apiKeyData = [
    {
        "service": f"service_{i}",
        "apiKey": f"apiKey_{i}",
        "secretKey": f"secretKey_{i}"
    }
    for i in range(5)
]

# 파일 실행 시마다 기존 데이터 삭제 후 새로 삽입
userInfo.delete_many({})
userToken.delete_many({})
apiKey.delete_many({})
print("\n- Cleared existing data in MongoDB.\n")

# userInfo 테이블에 유저 데이터 삽입
userInfo.insert_one(adminData)
userInfo.insert_many(userData)
print("- Inserted 50 userInfo into MongoDB.")

# token 테이블에 token 데이터 삽입
userToken.insert_many(token)
print("- Inserted 10 token into MongoDB.")

# apiKey 테이블에 apiKey 데이터 삽입
apiKey.insert_many(apiKeyData)
print("- Inserted 5 apiKey into MongoDB.\n")

# 메모리에 데이터가 남도록 반복적으로 조회 수행 (메모리 누출 시 더 많은 데이터가 노출될 가능성)
for i in range(100):
    list(db["userInfo"].find({}))
    list(db["token"].find({}))
    list(db["apiKey"].find({}))
print("- Simulated memory usage by performing multiple queries.\n")