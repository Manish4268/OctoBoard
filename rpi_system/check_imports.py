#!/usr/bin/env python3
"""Check Adafruit ADS1x15 library import paths"""

print("Checking Adafruit ADS1x15 library imports...")
print("=" * 60)

# Try different import methods
try:
    print("\n1. Trying: from adafruit_ads1x15.ads1115 import P0, P1, P2, P3")
    from adafruit_ads1x15.ads1115 import P0, P1, P2, P3
    print("   ✅ SUCCESS - P0, P1, P2, P3 found in ads1115")
    print(f"   P0={P0}, P1={P1}, P2={P2}, P3={P3}")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")

try:
    print("\n2. Trying: from adafruit_ads1x15.analog_in import P0, P1, P2, P3")
    from adafruit_ads1x15.analog_in import P0, P1, P2, P3
    print("   ✅ SUCCESS - P0, P1, P2, P3 found in analog_in")
    print(f"   P0={P0}, P1={P1}, P2={P2}, P3={P3}")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")

try:
    print("\n3. Checking analog_in module contents:")
    from adafruit_ads1x15 import analog_in
    contents = [x for x in dir(analog_in) if not x.startswith('_')]
    print(f"   Available: {contents}")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")

try:
    print("\n4. Checking ads1115 module contents:")
    from adafruit_ads1x15 import ads1115
    contents = [x for x in dir(ads1115) if not x.startswith('_')]
    print(f"   Available: {contents}")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")

print("\n" + "=" * 60)
print("Recommendation:")
print("Use the import method that shows '✅ SUCCESS' above")
