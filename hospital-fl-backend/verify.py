"""
System Verification and Setup Script
Ensures all components are properly configured before running
"""
import os
import sys
import subprocess

def verify_files():
    """Check all required files exist"""
    files = [
        'api.py', 'server.py', 'client.py', 'model.py',
        'data_loader.py', 'test_set.py', 'evaluator.py',
        'logger_config.py', 'generate_cert.py',
        'requirements.txt', 'README.md'
    ]
    
    print("\n=== VERIFYING FILES ===")
    missing = []
    for f in files:
        if os.path.exists(f):
            print(f"[OK] {f}")
        else:
            print(f"[FAIL] {f} MISSING")
            missing.append(f)
    
    return len(missing) == 0

def verify_imports():
    """Test all critical imports"""
    print("\n=== VERIFYING IMPORTS ===")
    imports = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'uvicorn'),
        ('torch', 'torch'),
        ('flwr', 'flwr'),
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('sklearn', 'scikit-learn'),
        ('cryptography', 'cryptography'),
    ]
    
    success = True
    for module, name in imports:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[FAIL] {name} NOT INSTALLED")
            success = False
    
    return success

def verify_tls_certs():
    """Check TLS certificates"""
    print("\n=== VERIFYING TLS CERTIFICATES ===")
    
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        print("[OK] cert.pem")
        print("[OK] key.pem")
        return True
    
    print("⚠ Certificates not found. Generating...")
    try:
        subprocess.run([sys.executable, 'generate_cert.py'], check=True)
        print("[OK] Certificates generated")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to generate: {e}")
        return False

def verify_model():
    """Test model loading"""
    print("\n=== VERIFYING MODEL ===")
    try:
        import torch
        from model import HealthNet
        
        net = HealthNet()
        x = torch.randn(1, 3)
        out = net(x)
        
        if out.shape == torch.Size([1, 1]) and 0 <= out.item() <= 1:
            print("[OK] Model inference works")
            print(f"  Input shape: {x.shape} → Output shape: {out.shape}")
            return True
        else:
            print(f"[FAIL] Unexpected output shape: {out.shape}")
            return False
    except Exception as e:
        print(f"[FAIL] Model error: {e}")
        return False

def verify_data_loader():
    """Test data loading"""
    print("\n=== VERIFYING DATA LOADER ===")
    try:
        from data_loader import get_hospital_dataset
        
        print("Loading dataset for Hospital_Test...")
        trainloader, testloader = get_hospital_dataset("Hospital_Test", test_size=0.2)
        
        print(f"✓ Data loaded")
        print(f"  Train batches: {len(trainloader)}")
        print(f"  Test batches: {len(testloader)}")
        
        return True
    except Exception as e:
        print(f"✗ Data loader error: {e}")
        return False

def main():
    print("=" * 70)
    print("HOSPITAL FL SYSTEM - VERIFICATION SCRIPT")
    print("=" * 70)
    
    checks = [
        ("Files", verify_files),
        ("Imports", verify_imports),
        ("TLS Certificates", verify_tls_certs),
        ("Model", verify_model),
        ("Data Loader", verify_data_loader),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n⚠ {name} check failed: {e}")
            results[name] = False
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_pass = all(results.values())
    
    if all_pass:
        print("\n✓ ALL CHECKS PASSED - SYSTEM READY")
        print("\nNext steps:")
        print("1. Terminal 1: python server.py")
        print("2. Terminal 2: uvicorn api:app --host 127.0.0.1 --port 8000")
        print("3. Terminal 3: npm run dev (in hospital-fl-app)")
        return 0
    else:
        print("\n✗ SOME CHECKS FAILED - FIX ISSUES ABOVE")
        print("\nCommon fixes:")
        print("- Run: pip install -r requirements.txt")
        print("- Run: python -m venv venv && .\\venv\\Scripts\\activate")
        return 1

if __name__ == "__main__":
    sys.exit(main())
