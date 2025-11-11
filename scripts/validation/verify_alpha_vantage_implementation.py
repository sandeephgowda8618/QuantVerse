#!/usr/bin/env python3
"""
Final Alpha Vantage Implementation Verification
Comprehensive verification of the Alpha Vantage implementation for QuantVerse uRISK
"""

import os
import sys
from datetime import datetime

def verify_implementation():
    """Verify all implementation components"""
    
    print("🔍" + "="*80 + "🔍")
    print("🏆 ALPHA VANTAGE IMPLEMENTATION VERIFICATION")
    print("🔍" + "="*80 + "🔍")
    print()
    
    # Check files exist
    required_files = {
        "top_200_companies.py": "Top 200 companies database",
        "enhanced_alpha_vantage_collector.py": "Main collector implementation", 
        "enhanced_alpha_vantage_schema.sql": "Enhanced database schema",
        "populate_alpha_vantage_data.py": "Data population orchestrator",
        "test_alpha_vantage_implementation.py": "Comprehensive test suite",
        "alpha_vantage_demo.py": "Quick demonstration script",
        "alpha_vantage_implementation_summary.py": "Implementation summary",
        "API_DOCS/Alpha Vantage.md": "Complete documentation"
    }
    
    print("📁 FILE VERIFICATION:")
    all_files_exist = True
    for filename, description in required_files.items():
        if os.path.exists(filename):
            file_size = os.path.getsize(filename) / 1024  # KB
            print(f"   ✅ {filename:<40} ({file_size:.1f} KB) - {description}")
        else:
            print(f"   ❌ {filename:<40} (MISSING) - {description}")
            all_files_exist = False
    
    print()
    
    # Test imports
    print("🔧 IMPORT VERIFICATION:")
    
    import_tests = [
        ("Top 200 Companies", "from top_200_companies import US_TRADEABLE_SYMBOLS, MEGA_CAP_SYMBOLS"),
        ("Alpha Vantage Config", "from enhanced_alpha_vantage_collector import get_alpha_vantage_config"),
        ("Alpha Vantage Functions", "from enhanced_alpha_vantage_collector import AlphaVantageFunction"),
    ]
    
    all_imports_work = True
    for test_name, import_statement in import_tests:
        try:
            exec(import_statement)
            print(f"   ✅ {test_name:<30} - Import successful")
        except Exception as e:
            print(f"   ❌ {test_name:<30} - Import failed: {e}")
            all_imports_work = False
    
    print()
    
    # Test data integrity
    print("📊 DATA INTEGRITY VERIFICATION:")
    
    try:
        sys.path.append('.')
        from top_200_companies import TOP_200_COMPANIES, US_TRADEABLE_SYMBOLS, MEGA_CAP_SYMBOLS, LARGE_CAP_SYMBOLS, MID_CAP_SYMBOLS
        
        data_checks = [
            ("Total Companies", len(TOP_200_COMPANIES), 200),
            ("US Tradeable Symbols", len(US_TRADEABLE_SYMBOLS), 150, 200),  # Range check
            ("Mega Cap Companies", len(MEGA_CAP_SYMBOLS), 20, 30),  # Range check
            ("Large Cap Companies", len(LARGE_CAP_SYMBOLS), 30, 80),  # Range check
            ("Mid Cap Companies", len(MID_CAP_SYMBOLS), 80, 120),  # Range check
        ]
        
        data_integrity_ok = True
        for check_name, actual, min_expected, max_expected=None in data_checks:
            if max_expected is None:
                # Exact check
                if actual == min_expected:
                    print(f"   ✅ {check_name:<25} - {actual} (expected: {min_expected})")
                else:
                    print(f"   ❌ {check_name:<25} - {actual} (expected: {min_expected})")
                    data_integrity_ok = False
            else:
                # Range check
                if min_expected <= actual <= max_expected:
                    print(f"   ✅ {check_name:<25} - {actual} (expected: {min_expected}-{max_expected})")
                else:
                    print(f"   ❌ {check_name:<25} - {actual} (expected: {min_expected}-{max_expected})")
                    data_integrity_ok = False
        
    except Exception as e:
        print(f"   ❌ Data integrity check failed: {e}")
        data_integrity_ok = False
    
    print()
    
    # Test API functions
    print("🔌 API FUNCTIONS VERIFICATION:")
    
    try:
        from enhanced_alpha_vantage_collector import AlphaVantageFunction
        functions = list(AlphaVantageFunction)
        
        function_categories = {
            "Stock APIs": ["TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY", "GLOBAL_QUOTE"],
            "Fundamental": ["OVERVIEW", "EARNINGS", "INCOME_STATEMENT"],
            "News & Intelligence": ["NEWS_SENTIMENT", "TOP_GAINERS_LOSERS"],
            "Forex": ["CURRENCY_EXCHANGE_RATE", "FX_DAILY"],
            "Crypto": ["DIGITAL_CURRENCY_DAILY"],
            "Commodities": ["WTI", "BRENT", "NATURAL_GAS"],
            "Economic": ["REAL_GDP", "CPI", "UNEMPLOYMENT"],
            "Technical": ["SMA", "EMA", "RSI", "MACD"]
        }
        
        api_functions_ok = True
        for category, sample_functions in function_categories.items():
            available_functions = [f.value for f in functions]
            found_functions = [f for f in sample_functions if f in available_functions]
            
            if len(found_functions) == len(sample_functions):
                print(f"   ✅ {category:<20} - All {len(sample_functions)} functions available")
            else:
                print(f"   ❌ {category:<20} - {len(found_functions)}/{len(sample_functions)} functions available")
                api_functions_ok = False
        
        print(f"   📊 Total API Functions: {len(functions)}")
        
    except Exception as e:
        print(f"   ❌ API functions check failed: {e}")
        api_functions_ok = False
    
    print()
    
    # Environment check
    print("🔧 ENVIRONMENT VERIFICATION:")
    
    env_checks = [
        ("ALPHA_VANTAGE_API_KEY", "Alpha Vantage API key"),
        ("DATABASE_URL", "Database connection string"),
    ]
    
    env_ready = True
    for env_var, description in env_checks:
        if os.getenv(env_var):
            value = os.getenv(env_var)
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"   ✅ {env_var:<25} - Set ({masked_value})")
        else:
            print(f"   ❌ {env_var:<25} - Not set ({description})")
            env_ready = False
    
    print()
    
    # Implementation status summary
    print("🎯 IMPLEMENTATION STATUS SUMMARY:")
    
    status_checks = [
        ("File Structure", all_files_exist),
        ("Import System", all_imports_work),
        ("Data Integrity", data_integrity_ok),
        ("API Functions", api_functions_ok),
        ("Environment", env_ready)
    ]
    
    total_checks = len(status_checks)
    passed_checks = sum([status for _, status in status_checks])
    
    for check_name, status in status_checks:
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {check_name:<20} - {'PASS' if status else 'FAIL'}")
    
    overall_success_rate = (passed_checks / total_checks) * 100
    
    print()
    print(f"📊 OVERALL SUCCESS RATE: {passed_checks}/{total_checks} ({overall_success_rate:.1f}%)")
    
    if overall_success_rate == 100:
        print("🎉 IMPLEMENTATION STATUS: PERFECT - Ready for production!")
    elif overall_success_rate >= 80:
        print("🟢 IMPLEMENTATION STATUS: EXCELLENT - Ready for testing!")
    elif overall_success_rate >= 60:
        print("🟡 IMPLEMENTATION STATUS: GOOD - Minor fixes needed")
    else:
        print("🔴 IMPLEMENTATION STATUS: NEEDS ATTENTION - Fix critical issues")
    
    print()
    
    # Next steps
    print("🚀 NEXT STEPS:")
    if not env_ready:
        print("   1. ⚙️  Set environment variables:")
        print("      export ALPHA_VANTAGE_API_KEY='your_api_key'")
        print("      export DATABASE_URL='postgresql://user:pass@host:port/db'")
    
    print("   2. 🧪 Run comprehensive test:")
    print("      python3 test_alpha_vantage_implementation.py")
    
    print("   3. 🎬 Try the quick demo:")
    print("      python3 alpha_vantage_demo.py")
    
    print("   4. 📊 Start data collection:")
    print("      python3 populate_alpha_vantage_data.py --tiers mega")
    
    print()
    print("🏆" + "="*80 + "🏆")
    print("✨ ALPHA VANTAGE IMPLEMENTATION VERIFICATION COMPLETE ✨")
    print("🏆" + "="*80 + "🏆")

def main():
    """Main execution"""
    verify_implementation()

if __name__ == "__main__":
    main()
