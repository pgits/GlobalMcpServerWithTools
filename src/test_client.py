import requests
import json

def test_health():
    response = requests.get("http://localhost:8888/health")
    print(f"Health check response: {response.json()}")
    assert response.status_code == 200

def test_create_doc():
    doc_data = {
        "title": "Test Document",
        "content": "This is a test document created by the MCP Tools Server."
    }
    
    response = requests.post(
        "http://localhost:8888/create_doc",
        json=doc_data
    )
    print(f"Create doc response: {response.json() if response.ok else response.text}")
    print(f"Status code: {response.status_code}")

if __name__ == "__main__":
    print("Testing MCP Tools Server...")
    
    try:
        test_health()
        print("\nHealth check passed!")
    except Exception as e:
        print(f"\nHealth check failed: {str(e)}")
    
    try:
        test_create_doc()
        print("\nDocument creation test completed!")
    except Exception as e:
        print(f"\nDocument creation test failed: {str(e)}")
