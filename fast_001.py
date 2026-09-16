import uvicorn
from fastapi import FastAPI
app = FastAPI()
@app.get("/users")
def read_users():
    return get_users()

def get_users():
    return [{"name": "Alice"}, {"name": "Bob"}]
#uvicorn:轻量级的web服务器
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
