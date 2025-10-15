import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    r = requests.get(f'{BASE_URL}/health')
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')

def test_recommendation():
    """Test product recommendation endpoint"""
    print("\n=== Testing Product Recommendation ===")
    
    # Example customer features (replace with real feature values from your model)
    sample_request = {
        'customer_id': 12345,
        'features': {
            'age': 35,
            'renta': 100000.0,
            'antiguedad': 120,
            'month': 5,
            'segmento': 1,
            # Add more features as required by your model
        },
        'owned_products': ['ind_cco_fin_ult1'],  # Products already owned
        'k': 7,  # Top 7 recommendations
        'return_scores': True  # Include prediction scores
    }
    
    r = requests.post(f'{BASE_URL}/recommend', json=sample_request)
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')

def test_shap_explanation():
    """Test SHAP explanation endpoint"""
    print("\n=== Testing SHAP Explanation ===")
    
    sample_request = {
        'customer_id': 12345,
        'features': {
            'age': 35,
            'renta': 100000.0,
            'antiguedad': 120,
            'month': 5,
            'segmento': 1,
            # Add more features as required by your model
        },
        'product': 'ind_cco_fin_ult1'  # Product to explain
    }
    
    r = requests.post(f'{BASE_URL}/explain', json=sample_request)
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')

def test_fairness():
    """Test fairness evaluation endpoint"""
    print("\n=== Testing Fairness Evaluation ===")
    
    # Example: test fairness across age groups
    sample_request = {
        'customer_features_list': [
            {'age': 25, 'renta': 50000, 'antiguedad': 60, 'month': 5, 'segmento': 1},
            {'age': 25, 'renta': 55000, 'antiguedad': 65, 'month': 5, 'segmento': 1},
            {'age': 45, 'renta': 100000, 'antiguedad': 120, 'month': 5, 'segmento': 2},
            {'age': 45, 'renta': 95000, 'antiguedad': 115, 'month': 5, 'segmento': 2},
            {'age': 65, 'renta': 70000, 'antiguedad': 180, 'month': 5, 'segmento': 3},
            {'age': 65, 'renta': 75000, 'antiguedad': 185, 'month': 5, 'segmento': 3},
        ],
        'demographic_attribute': 'age',  # Can be 'age', 'gender', or 'income'
        'k': 7
    }
    
    r = requests.post(f'{BASE_URL}/fairness', json=sample_request)
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')

if __name__ == '__main__':
    try:
        # Test all endpoints
        test_health()
        test_recommendation()
        test_shap_explanation()
        test_fairness()
        
        print("\n✓ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API. Make sure the server is running:")
        print("   uvicorn app:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\nError: {e}")
