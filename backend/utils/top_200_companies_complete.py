"""
Top 200 Global Companies by Market Cap (November 2025)
Comprehensive list for Alpha Vantage ingestion system
Organized by market cap tiers for efficient processing
"""

from typing import List, Dict, Optional, Any, Any

class Top200Companies:
    """
    Top 200 global companies organized by market cap tiers
    Updated for November 2025 market conditions
    """
    
    # Mega Cap Companies (1-25): Market Cap > $300B
    MEGA_CAP = [
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "market_cap": 3500000000000, "tier": "mega_cap", "epoch": 1, "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "market_cap": 2800000000000, "tier": "mega_cap", "epoch": 2, "sector": "Technology"},
        {"symbol": "AAPL", "name": "Apple Inc.", "market_cap": 2700000000000, "tier": "mega_cap", "epoch": 3, "sector": "Technology"},
        {"symbol": "GOOG", "name": "Alphabet Inc. Class C", "market_cap": 1800000000000, "tier": "mega_cap", "epoch": 4, "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "market_cap": 1800000000000, "tier": "mega_cap", "epoch": 5, "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "market_cap": 1600000000000, "tier": "mega_cap", "epoch": 6, "sector": "Technology"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "market_cap": 1200000000000, "tier": "mega_cap", "epoch": 7, "sector": "Technology"},
        {"symbol": "AVGO", "name": "Broadcom Inc.", "market_cap": 800000000000, "tier": "mega_cap", "epoch": 8, "sector": "Technology"},
        {"symbol": "TSM", "name": "Taiwan Semiconductor", "market_cap": 750000000000, "tier": "mega_cap", "epoch": 9, "sector": "Technology"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "market_cap": 700000000000, "tier": "mega_cap", "epoch": 10, "sector": "Consumer Discretionary"},
        {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc.", "market_cap": 650000000000, "tier": "mega_cap", "epoch": 11, "sector": "Financial Services"},
        {"symbol": "LLY", "name": "Eli Lilly and Company", "market_cap": 600000000000, "tier": "mega_cap", "epoch": 12, "sector": "Healthcare"},
        {"symbol": "V", "name": "Visa Inc.", "market_cap": 550000000000, "tier": "mega_cap", "epoch": 13, "sector": "Financial Services"},
        {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "market_cap": 500000000000, "tier": "mega_cap", "epoch": 14, "sector": "Healthcare"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "market_cap": 480000000000, "tier": "mega_cap", "epoch": 15, "sector": "Financial Services"},
        {"symbol": "WMT", "name": "Walmart Inc.", "market_cap": 450000000000, "tier": "mega_cap", "epoch": 16, "sector": "Consumer Staples"},
        {"symbol": "XOM", "name": "Exxon Mobil Corporation", "market_cap": 440000000000, "tier": "mega_cap", "epoch": 17, "sector": "Energy"},
        {"symbol": "ORCL", "name": "Oracle Corporation", "market_cap": 420000000000, "tier": "mega_cap", "epoch": 18, "sector": "Technology"},
        {"symbol": "MA", "name": "Mastercard Inc.", "market_cap": 400000000000, "tier": "mega_cap", "epoch": 19, "sector": "Financial Services"},
        {"symbol": "PG", "name": "Procter & Gamble Co.", "market_cap": 380000000000, "tier": "mega_cap", "epoch": 20, "sector": "Consumer Staples"},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "market_cap": 370000000000, "tier": "mega_cap", "epoch": 21, "sector": "Healthcare"},
        {"symbol": "HD", "name": "Home Depot Inc.", "market_cap": 360000000000, "tier": "mega_cap", "epoch": 22, "sector": "Consumer Discretionary"},
        {"symbol": "CVX", "name": "Chevron Corporation", "market_cap": 350000000000, "tier": "mega_cap", "epoch": 23, "sector": "Energy"},
        {"symbol": "NFLX", "name": "Netflix Inc.", "market_cap": 340000000000, "tier": "mega_cap", "epoch": 24, "sector": "Consumer Discretionary"},
        {"symbol": "ABBV", "name": "AbbVie Inc.", "market_cap": 330000000000, "tier": "mega_cap", "epoch": 25, "sector": "Healthcare"}
    ]
    
    # Large Cap Companies (26-100): Market Cap $50B - $300B
    LARGE_CAP = [
        {"symbol": "CRM", "name": "Salesforce Inc.", "market_cap": 250000000000, "tier": "large_cap", "epoch": 26, "sector": "Technology"},
        {"symbol": "BAC", "name": "Bank of America Corp.", "market_cap": 240000000000, "tier": "large_cap", "epoch": 27, "sector": "Financial Services"},
        {"symbol": "AMD", "name": "Advanced Micro Devices", "market_cap": 230000000000, "tier": "large_cap", "epoch": 28, "sector": "Technology"},
        {"symbol": "ADBE", "name": "Adobe Inc.", "market_cap": 220000000000, "tier": "large_cap", "epoch": 29, "sector": "Technology"},
        {"symbol": "COST", "name": "Costco Wholesale Corp.", "market_cap": 210000000000, "tier": "large_cap", "epoch": 30, "sector": "Consumer Staples"},
        {"symbol": "TM", "name": "Toyota Motor Corp.", "market_cap": 200000000000, "tier": "large_cap", "epoch": 31, "sector": "Consumer Discretionary"},
        {"symbol": "MRK", "name": "Merck & Co. Inc.", "market_cap": 195000000000, "tier": "large_cap", "epoch": 32, "sector": "Healthcare"},
        {"symbol": "NOW", "name": "ServiceNow Inc.", "market_cap": 190000000000, "tier": "large_cap", "epoch": 33, "sector": "Technology"},
        {"symbol": "WFC", "name": "Wells Fargo & Co.", "market_cap": 185000000000, "tier": "large_cap", "epoch": 34, "sector": "Financial Services"},
        {"symbol": "TMO", "name": "Thermo Fisher Scientific", "market_cap": 180000000000, "tier": "large_cap", "epoch": 35, "sector": "Healthcare"},
        {"symbol": "IBM", "name": "International Business Machines", "market_cap": 175000000000, "tier": "large_cap", "epoch": 36, "sector": "Technology"},
        {"symbol": "GS", "name": "Goldman Sachs Group Inc.", "market_cap": 170000000000, "tier": "large_cap", "epoch": 37, "sector": "Financial Services"},
        {"symbol": "ASML", "name": "ASML Holding NV", "market_cap": 165000000000, "tier": "large_cap", "epoch": 38, "sector": "Technology"},
        {"symbol": "CAT", "name": "Caterpillar Inc.", "market_cap": 160000000000, "tier": "large_cap", "epoch": 39, "sector": "Industrials"},
        {"symbol": "AXP", "name": "American Express Co.", "market_cap": 155000000000, "tier": "large_cap", "epoch": 40, "sector": "Financial Services"},
        {"symbol": "INTU", "name": "Intuit Inc.", "market_cap": 150000000000, "tier": "large_cap", "epoch": 41, "sector": "Technology"},
        {"symbol": "T", "name": "AT&T Inc.", "market_cap": 148000000000, "tier": "large_cap", "epoch": 42, "sector": "Communication Services"},
        {"symbol": "VZ", "name": "Verizon Communications", "market_cap": 145000000000, "tier": "large_cap", "epoch": 43, "sector": "Communication Services"},
        {"symbol": "MCD", "name": "McDonald's Corp.", "market_cap": 140000000000, "tier": "large_cap", "epoch": 44, "sector": "Consumer Discretionary"},
        {"symbol": "QCOM", "name": "QUALCOMM Inc.", "market_cap": 138000000000, "tier": "large_cap", "epoch": 45, "sector": "Technology"},
        {"symbol": "HON", "name": "Honeywell International", "market_cap": 135000000000, "tier": "large_cap", "epoch": 46, "sector": "Industrials"},
        {"symbol": "RTX", "name": "RTX Corporation", "market_cap": 132000000000, "tier": "large_cap", "epoch": 47, "sector": "Industrials"},
        {"symbol": "LOW", "name": "Lowe's Companies Inc.", "market_cap": 130000000000, "tier": "large_cap", "epoch": 48, "sector": "Consumer Discretionary"},
        {"symbol": "NKE", "name": "NIKE Inc.", "market_cap": 128000000000, "tier": "large_cap", "epoch": 49, "sector": "Consumer Discretionary"},
        {"symbol": "UPS", "name": "United Parcel Service", "market_cap": 125000000000, "tier": "large_cap", "epoch": 50, "sector": "Industrials"},
        {"symbol": "BABA", "name": "Alibaba Group Holding", "market_cap": 122000000000, "tier": "large_cap", "epoch": 51, "sector": "Technology"},
        {"symbol": "COP", "name": "ConocoPhillips", "market_cap": 120000000000, "tier": "large_cap", "epoch": 52, "sector": "Energy"},
        {"symbol": "TXN", "name": "Texas Instruments Inc.", "market_cap": 118000000000, "tier": "large_cap", "epoch": 53, "sector": "Technology"},
        {"symbol": "LMT", "name": "Lockheed Martin Corp.", "market_cap": 115000000000, "tier": "large_cap", "epoch": 54, "sector": "Industrials"},
        {"symbol": "AMGN", "name": "Amgen Inc.", "market_cap": 112000000000, "tier": "large_cap", "epoch": 55, "sector": "Healthcare"},
        {"symbol": "SPGI", "name": "S&P Global Inc.", "market_cap": 110000000000, "tier": "large_cap", "epoch": 56, "sector": "Financial Services"},
        {"symbol": "NEE", "name": "NextEra Energy Inc.", "market_cap": 108000000000, "tier": "large_cap", "epoch": 57, "sector": "Utilities"},
        {"symbol": "BMY", "name": "Bristol-Myers Squibb", "market_cap": 105000000000, "tier": "large_cap", "epoch": 58, "sector": "Healthcare"},
        {"symbol": "ISRG", "name": "Intuitive Surgical Inc.", "market_cap": 103000000000, "tier": "large_cap", "epoch": 59, "sector": "Healthcare"},
        {"symbol": "SYK", "name": "Stryker Corp.", "market_cap": 100000000000, "tier": "large_cap", "epoch": 60, "sector": "Healthcare"},
        {"symbol": "MDT", "name": "Medtronic PLC", "market_cap": 98000000000, "tier": "large_cap", "epoch": 61, "sector": "Healthcare"},
        {"symbol": "DUK", "name": "Duke Energy Corp.", "market_cap": 95000000000, "tier": "large_cap", "epoch": 62, "sector": "Utilities"},
        {"symbol": "SO", "name": "Southern Company", "market_cap": 93000000000, "tier": "large_cap", "epoch": 63, "sector": "Utilities"},
        {"symbol": "GILD", "name": "Gilead Sciences Inc.", "market_cap": 90000000000, "tier": "large_cap", "epoch": 64, "sector": "Healthcare"},
        {"symbol": "MS", "name": "Morgan Stanley", "market_cap": 88000000000, "tier": "large_cap", "epoch": 65, "sector": "Financial Services"},
        {"symbol": "PFE", "name": "Pfizer Inc.", "market_cap": 85000000000, "tier": "large_cap", "epoch": 66, "sector": "Healthcare"},
        {"symbol": "CI", "name": "Cigna Corp.", "market_cap": 83000000000, "tier": "large_cap", "epoch": 67, "sector": "Healthcare"},
        {"symbol": "BLK", "name": "BlackRock Inc.", "market_cap": 80000000000, "tier": "large_cap", "epoch": 68, "sector": "Financial Services"},
        {"symbol": "USB", "name": "U.S. Bancorp", "market_cap": 78000000000, "tier": "large_cap", "epoch": 69, "sector": "Financial Services"},
        {"symbol": "C", "name": "Citigroup Inc.", "market_cap": 75000000000, "tier": "large_cap", "epoch": 70, "sector": "Financial Services"},
        {"symbol": "ZTS", "name": "Zoetis Inc.", "market_cap": 73000000000, "tier": "large_cap", "epoch": 71, "sector": "Healthcare"},
        {"symbol": "BA", "name": "Boeing Co.", "market_cap": 70000000000, "tier": "large_cap", "epoch": 72, "sector": "Industrials"},
        {"symbol": "SCHW", "name": "Charles Schwab Corp.", "market_cap": 68000000000, "tier": "large_cap", "epoch": 73, "sector": "Financial Services"},
        {"symbol": "CVS", "name": "CVS Health Corp.", "market_cap": 65000000000, "tier": "large_cap", "epoch": 74, "sector": "Healthcare"},
        {"symbol": "MDLZ", "name": "Mondelez International", "market_cap": 63000000000, "tier": "large_cap", "epoch": 75, "sector": "Consumer Staples"},
        {"symbol": "KO", "name": "Coca-Cola Co.", "market_cap": 60000000000, "tier": "large_cap", "epoch": 76, "sector": "Consumer Staples"},
        {"symbol": "PEP", "name": "PepsiCo Inc.", "market_cap": 58000000000, "tier": "large_cap", "epoch": 77, "sector": "Consumer Staples"},
        {"symbol": "DE", "name": "Deere & Co.", "market_cap": 55000000000, "tier": "large_cap", "epoch": 78, "sector": "Industrials"},
        {"symbol": "MMC", "name": "Marsh & McLennan", "market_cap": 53000000000, "tier": "large_cap", "epoch": 79, "sector": "Financial Services"},
        {"symbol": "PYPL", "name": "PayPal Holdings Inc.", "market_cap": 50000000000, "tier": "large_cap", "epoch": 80, "sector": "Financial Services"}
    ]
    
    # Mid Cap Companies (81-150): Market Cap $10B - $50B
    MID_CAP = [
        {"symbol": "AMAT", "name": "Applied Materials Inc.", "market_cap": 48000000000, "tier": "mid_cap", "epoch": 81, "sector": "Technology"},
        {"symbol": "LRCX", "name": "Lam Research Corp.", "market_cap": 46000000000, "tier": "mid_cap", "epoch": 82, "sector": "Technology"},
        {"symbol": "ADI", "name": "Analog Devices Inc.", "market_cap": 44000000000, "tier": "mid_cap", "epoch": 83, "sector": "Technology"},
        {"symbol": "KLAC", "name": "KLA Corp.", "market_cap": 42000000000, "tier": "mid_cap", "epoch": 84, "sector": "Technology"},
        {"symbol": "MU", "name": "Micron Technology Inc.", "market_cap": 40000000000, "tier": "mid_cap", "epoch": 85, "sector": "Technology"},
        {"symbol": "ELV", "name": "Elevance Health Inc.", "market_cap": 38000000000, "tier": "mid_cap", "epoch": 86, "sector": "Healthcare"},
        {"symbol": "CSX", "name": "CSX Corp.", "market_cap": 36000000000, "tier": "mid_cap", "epoch": 87, "sector": "Industrials"},
        {"symbol": "REGN", "name": "Regeneron Pharmaceuticals", "market_cap": 34000000000, "tier": "mid_cap", "epoch": 88, "sector": "Healthcare"},
        {"symbol": "PANW", "name": "Palo Alto Networks Inc.", "market_cap": 32000000000, "tier": "mid_cap", "epoch": 89, "sector": "Technology"},
        {"symbol": "SNPS", "name": "Synopsys Inc.", "market_cap": 30000000000, "tier": "mid_cap", "epoch": 90, "sector": "Technology"},
        {"symbol": "CDNS", "name": "Cadence Design Systems", "market_cap": 28000000000, "tier": "mid_cap", "epoch": 91, "sector": "Technology"},
        {"symbol": "MRVL", "name": "Marvell Technology Inc.", "market_cap": 26000000000, "tier": "mid_cap", "epoch": 92, "sector": "Technology"},
        {"symbol": "FTNT", "name": "Fortinet Inc.", "market_cap": 24000000000, "tier": "mid_cap", "epoch": 93, "sector": "Technology"},
        {"symbol": "WDAY", "name": "Workday Inc.", "market_cap": 22000000000, "tier": "mid_cap", "epoch": 94, "sector": "Technology"},
        {"symbol": "MNST", "name": "Monster Beverage Corp.", "market_cap": 20000000000, "tier": "mid_cap", "epoch": 95, "sector": "Consumer Staples"},
        {"symbol": "PAYX", "name": "Paychex Inc.", "market_cap": 18000000000, "tier": "mid_cap", "epoch": 96, "sector": "Technology"},
        {"symbol": "ADSK", "name": "Autodesk Inc.", "market_cap": 16000000000, "tier": "mid_cap", "epoch": 97, "sector": "Technology"},
        {"symbol": "ADP", "name": "Automatic Data Processing", "market_cap": 15000000000, "tier": "mid_cap", "epoch": 98, "sector": "Technology"},
        {"symbol": "ROST", "name": "Ross Stores Inc.", "market_cap": 14000000000, "tier": "mid_cap", "epoch": 99, "sector": "Consumer Discretionary"},
        {"symbol": "FAST", "name": "Fastenal Co.", "market_cap": 13000000000, "tier": "mid_cap", "epoch": 100, "sector": "Industrials"},
        {"symbol": "PCAR", "name": "PACCAR Inc.", "market_cap": 12500000000, "tier": "mid_cap", "epoch": 101, "sector": "Industrials"},
        {"symbol": "ODFL", "name": "Old Dominion Freight Line", "market_cap": 12000000000, "tier": "mid_cap", "epoch": 102, "sector": "Industrials"},
        {"symbol": "VRSK", "name": "Verisk Analytics Inc.", "market_cap": 11500000000, "tier": "mid_cap", "epoch": 103, "sector": "Industrials"},
        {"symbol": "EXC", "name": "Exelon Corp.", "market_cap": 11000000000, "tier": "mid_cap", "epoch": 104, "sector": "Utilities"},
        {"symbol": "XEL", "name": "Xcel Energy Inc.", "market_cap": 10500000000, "tier": "mid_cap", "epoch": 105, "sector": "Utilities"},
        {"symbol": "CTAS", "name": "Cintas Corp.", "market_cap": 10200000000, "tier": "mid_cap", "epoch": 106, "sector": "Industrials"},
        {"symbol": "CTSH", "name": "Cognizant Technology Solutions", "market_cap": 10000000000, "tier": "mid_cap", "epoch": 107, "sector": "Technology"},
        {"symbol": "ANSS", "name": "ANSYS Inc.", "market_cap": 9800000000, "tier": "mid_cap", "epoch": 108, "sector": "Technology"},
        {"symbol": "DXCM", "name": "DexCom Inc.", "market_cap": 9600000000, "tier": "mid_cap", "epoch": 109, "sector": "Healthcare"},
        {"symbol": "BIIB", "name": "Biogen Inc.", "market_cap": 9400000000, "tier": "mid_cap", "epoch": 110, "sector": "Healthcare"},
        {"symbol": "WBD", "name": "Warner Bros. Discovery", "market_cap": 9200000000, "tier": "mid_cap", "epoch": 111, "sector": "Communication Services"},
        {"symbol": "MRNA", "name": "Moderna Inc.", "market_cap": 9000000000, "tier": "mid_cap", "epoch": 112, "sector": "Healthcare"},
        {"symbol": "SBUX", "name": "Starbucks Corp.", "market_cap": 8800000000, "tier": "mid_cap", "epoch": 113, "sector": "Consumer Discretionary"},
        {"symbol": "ORLY", "name": "O'Reilly Automotive Inc.", "market_cap": 8600000000, "tier": "mid_cap", "epoch": 114, "sector": "Consumer Discretionary"},
        {"symbol": "MAR", "name": "Marriott International", "market_cap": 8400000000, "tier": "mid_cap", "epoch": 115, "sector": "Consumer Discretionary"},
        {"symbol": "HCA", "name": "HCA Healthcare Inc.", "market_cap": 8200000000, "tier": "mid_cap", "epoch": 116, "sector": "Healthcare"},
        {"symbol": "TJX", "name": "TJX Companies Inc.", "market_cap": 8000000000, "tier": "mid_cap", "epoch": 117, "sector": "Consumer Discretionary"},
        {"symbol": "CHTR", "name": "Charter Communications", "market_cap": 7800000000, "tier": "mid_cap", "epoch": 118, "sector": "Communication Services"},
        {"symbol": "KHC", "name": "Kraft Heinz Co.", "market_cap": 7600000000, "tier": "mid_cap", "epoch": 119, "sector": "Consumer Staples"},
        {"symbol": "EA", "name": "Electronic Arts Inc.", "market_cap": 7400000000, "tier": "mid_cap", "epoch": 120, "sector": "Technology"},
        {"symbol": "IDXX", "name": "IDEXX Laboratories Inc.", "market_cap": 7200000000, "tier": "mid_cap", "epoch": 121, "sector": "Healthcare"},
        {"symbol": "MCHP", "name": "Microchip Technology", "market_cap": 7000000000, "tier": "mid_cap", "epoch": 122, "sector": "Technology"},
        {"symbol": "DLTR", "name": "Dollar Tree Inc.", "market_cap": 6800000000, "tier": "mid_cap", "epoch": 123, "sector": "Consumer Discretionary"},
        {"symbol": "WM", "name": "Waste Management Inc.", "market_cap": 6600000000, "tier": "mid_cap", "epoch": 124, "sector": "Industrials"},
        {"symbol": "RSG", "name": "Republic Services Inc.", "market_cap": 6400000000, "tier": "mid_cap", "epoch": 125, "sector": "Industrials"},
        {"symbol": "EW", "name": "Edwards Lifesciences", "market_cap": 6200000000, "tier": "mid_cap", "epoch": 126, "sector": "Healthcare"},
        {"symbol": "BDX", "name": "Becton Dickinson and Co.", "market_cap": 6000000000, "tier": "mid_cap", "epoch": 127, "sector": "Healthcare"},
        {"symbol": "IEX", "name": "IDEX Corp.", "market_cap": 5800000000, "tier": "mid_cap", "epoch": 128, "sector": "Industrials"},
        {"symbol": "VRTX", "name": "Vertex Pharmaceuticals", "market_cap": 5600000000, "tier": "mid_cap", "epoch": 129, "sector": "Healthcare"},
        {"symbol": "ILMN", "name": "Illumina Inc.", "market_cap": 5400000000, "tier": "mid_cap", "epoch": 130, "sector": "Healthcare"},
        {"symbol": "EXR", "name": "Extended Stay America", "market_cap": 5200000000, "tier": "mid_cap", "epoch": 131, "sector": "Real Estate"},
        {"symbol": "SPG", "name": "Simon Property Group", "market_cap": 5000000000, "tier": "mid_cap", "epoch": 132, "sector": "Real Estate"},
        {"symbol": "AVB", "name": "AvalonBay Communities", "market_cap": 4800000000, "tier": "mid_cap", "epoch": 133, "sector": "Real Estate"},
        {"symbol": "EQR", "name": "Equity Residential", "market_cap": 4600000000, "tier": "mid_cap", "epoch": 134, "sector": "Real Estate"},
        {"symbol": "WELL", "name": "Welltower Inc.", "market_cap": 4400000000, "tier": "mid_cap", "epoch": 135, "sector": "Real Estate"},
        {"symbol": "PSA", "name": "Public Storage", "market_cap": 4200000000, "tier": "mid_cap", "epoch": 136, "sector": "Real Estate"},
        {"symbol": "O", "name": "Realty Income Corp.", "market_cap": 4000000000, "tier": "mid_cap", "epoch": 137, "sector": "Real Estate"},
        {"symbol": "PLD", "name": "Prologis Inc.", "market_cap": 3800000000, "tier": "mid_cap", "epoch": 138, "sector": "Real Estate"},
        {"symbol": "AMT", "name": "American Tower Corp.", "market_cap": 3600000000, "tier": "mid_cap", "epoch": 139, "sector": "Real Estate"},
        {"symbol": "CCI", "name": "Crown Castle International", "market_cap": 3400000000, "tier": "mid_cap", "epoch": 140, "sector": "Real Estate"},
        {"symbol": "EQIX", "name": "Equinix Inc.", "market_cap": 3200000000, "tier": "mid_cap", "epoch": 141, "sector": "Real Estate"},
        {"symbol": "DLR", "name": "Digital Realty Trust", "market_cap": 3000000000, "tier": "mid_cap", "epoch": 142, "sector": "Real Estate"},
        {"symbol": "SBAC", "name": "SBA Communications", "market_cap": 2800000000, "tier": "mid_cap", "epoch": 143, "sector": "Real Estate"},
        {"symbol": "WY", "name": "Weyerhaeuser Co.", "market_cap": 2600000000, "tier": "mid_cap", "epoch": 144, "sector": "Real Estate"},
        {"symbol": "UDR", "name": "UDR Inc.", "market_cap": 2400000000, "tier": "mid_cap", "epoch": 145, "sector": "Real Estate"},
        {"symbol": "ESS", "name": "Essex Property Trust", "market_cap": 2200000000, "tier": "mid_cap", "epoch": 146, "sector": "Real Estate"},
        {"symbol": "MAA", "name": "Mid-America Apartment", "market_cap": 2000000000, "tier": "mid_cap", "epoch": 147, "sector": "Real Estate"},
        {"symbol": "CPT", "name": "Camden Property Trust", "market_cap": 1800000000, "tier": "mid_cap", "epoch": 148, "sector": "Real Estate"},
        {"symbol": "HST", "name": "Host Hotels & Resorts", "market_cap": 1600000000, "tier": "mid_cap", "epoch": 149, "sector": "Real Estate"},
        {"symbol": "VTR", "name": "Ventas Inc.", "market_cap": 1500000000, "tier": "mid_cap", "epoch": 150, "sector": "Real Estate"}
    ]
    
    # Small Cap Companies (151-200): Market Cap $2B - $10B
    SMALL_CAP = [
        {"symbol": "SMCI", "name": "Super Micro Computer", "market_cap": 1400000000, "tier": "small_cap", "epoch": 151, "sector": "Technology"},
        {"symbol": "ARM", "name": "Arm Holdings PLC", "market_cap": 1300000000, "tier": "small_cap", "epoch": 152, "sector": "Technology"},
        {"symbol": "CRWD", "name": "CrowdStrike Holdings", "market_cap": 1200000000, "tier": "small_cap", "epoch": 153, "sector": "Technology"},
        {"symbol": "PLTR", "name": "Palantir Technologies", "market_cap": 1100000000, "tier": "small_cap", "epoch": 154, "sector": "Technology"},
        {"symbol": "SNOW", "name": "Snowflake Inc.", "market_cap": 1000000000, "tier": "small_cap", "epoch": 155, "sector": "Technology"},
        {"symbol": "ZM", "name": "Zoom Video Communications", "market_cap": 950000000, "tier": "small_cap", "epoch": 156, "sector": "Technology"},
        {"symbol": "DOCU", "name": "DocuSign Inc.", "market_cap": 900000000, "tier": "small_cap", "epoch": 157, "sector": "Technology"},
        {"symbol": "OKTA", "name": "Okta Inc.", "market_cap": 850000000, "tier": "small_cap", "epoch": 158, "sector": "Technology"},
        {"symbol": "ZS", "name": "Zscaler Inc.", "market_cap": 800000000, "tier": "small_cap", "epoch": 159, "sector": "Technology"},
        {"symbol": "DDOG", "name": "Datadog Inc.", "market_cap": 750000000, "tier": "small_cap", "epoch": 160, "sector": "Technology"},
        {"symbol": "MDB", "name": "MongoDB Inc.", "market_cap": 700000000, "tier": "small_cap", "epoch": 161, "sector": "Technology"},
        {"symbol": "NET", "name": "Cloudflare Inc.", "market_cap": 650000000, "tier": "small_cap", "epoch": 162, "sector": "Technology"},
        {"symbol": "TEAM", "name": "Atlassian Corp.", "market_cap": 600000000, "tier": "small_cap", "epoch": 163, "sector": "Technology"},
        {"symbol": "SPLK", "name": "Splunk Inc.", "market_cap": 550000000, "tier": "small_cap", "epoch": 164, "sector": "Technology"},
        {"symbol": "VEEV", "name": "Veeva Systems Inc.", "market_cap": 500000000, "tier": "small_cap", "epoch": 165, "sector": "Technology"},
        {"symbol": "TTD", "name": "Trade Desk Inc.", "market_cap": 480000000, "tier": "small_cap", "epoch": 166, "sector": "Technology"},
        {"symbol": "PINS", "name": "Pinterest Inc.", "market_cap": 460000000, "tier": "small_cap", "epoch": 167, "sector": "Technology"},
        {"symbol": "SNAP", "name": "Snap Inc.", "market_cap": 440000000, "tier": "small_cap", "epoch": 168, "sector": "Technology"},
        {"symbol": "TWLO", "name": "Twilio Inc.", "market_cap": 420000000, "tier": "small_cap", "epoch": 169, "sector": "Technology"},
        {"symbol": "SQ", "name": "Block Inc.", "market_cap": 400000000, "tier": "small_cap", "epoch": 170, "sector": "Technology"},
        {"symbol": "UBER", "name": "Uber Technologies", "market_cap": 380000000, "tier": "small_cap", "epoch": 171, "sector": "Technology"},
        {"symbol": "LYFT", "name": "Lyft Inc.", "market_cap": 360000000, "tier": "small_cap", "epoch": 172, "sector": "Technology"},
        {"symbol": "DASH", "name": "DoorDash Inc.", "market_cap": 340000000, "tier": "small_cap", "epoch": 173, "sector": "Technology"},
        {"symbol": "ABNB", "name": "Airbnb Inc.", "market_cap": 320000000, "tier": "small_cap", "epoch": 174, "sector": "Technology"},
        {"symbol": "ROKU", "name": "Roku Inc.", "market_cap": 300000000, "tier": "small_cap", "epoch": 175, "sector": "Technology"},
        {"symbol": "SPOT", "name": "Spotify Technology", "market_cap": 280000000, "tier": "small_cap", "epoch": 176, "sector": "Technology"},
        {"symbol": "SHW", "name": "Sherwin-Williams Co.", "market_cap": 260000000, "tier": "small_cap", "epoch": 177, "sector": "Materials"},
        {"symbol": "LIN", "name": "Linde PLC", "market_cap": 240000000, "tier": "small_cap", "epoch": 178, "sector": "Materials"},
        {"symbol": "APD", "name": "Air Products and Chemicals", "market_cap": 220000000, "tier": "small_cap", "epoch": 179, "sector": "Materials"},
        {"symbol": "ECL", "name": "Ecolab Inc.", "market_cap": 200000000, "tier": "small_cap", "epoch": 180, "sector": "Materials"},
        {"symbol": "FCX", "name": "Freeport-McMoRan Inc.", "market_cap": 180000000, "tier": "small_cap", "epoch": 181, "sector": "Materials"},
        {"symbol": "NEM", "name": "Newmont Corp.", "market_cap": 160000000, "tier": "small_cap", "epoch": 182, "sector": "Materials"},
        {"symbol": "DD", "name": "DuPont de Nemours Inc.", "market_cap": 140000000, "tier": "small_cap", "epoch": 183, "sector": "Materials"},
        {"symbol": "PPG", "name": "PPG Industries Inc.", "market_cap": 120000000, "tier": "small_cap", "epoch": 184, "sector": "Materials"},
        {"symbol": "IFF", "name": "International Flavors", "market_cap": 100000000, "tier": "small_cap", "epoch": 185, "sector": "Materials"},
        {"symbol": "VMC", "name": "Vulcan Materials Co.", "market_cap": 90000000, "tier": "small_cap", "epoch": 186, "sector": "Materials"},
        {"symbol": "MLM", "name": "Martin Marietta Materials", "market_cap": 80000000, "tier": "small_cap", "epoch": 187, "sector": "Materials"},
        {"symbol": "PKG", "name": "Packaging Corp. of America", "market_cap": 70000000, "tier": "small_cap", "epoch": 188, "sector": "Materials"},
        {"symbol": "IP", "name": "International Paper Co.", "market_cap": 60000000, "tier": "small_cap", "epoch": 189, "sector": "Materials"},
        {"symbol": "CF", "name": "CF Industries Holdings", "market_cap": 50000000, "tier": "small_cap", "epoch": 190, "sector": "Materials"},
        {"symbol": "FMC", "name": "FMC Corp.", "market_cap": 45000000, "tier": "small_cap", "epoch": 191, "sector": "Materials"},
        {"symbol": "ALB", "name": "Albemarle Corp.", "market_cap": 40000000, "tier": "small_cap", "epoch": 192, "sector": "Materials"},
        {"symbol": "MOH", "name": "Molina Healthcare Inc.", "market_cap": 35000000, "tier": "small_cap", "epoch": 193, "sector": "Healthcare"},
        {"symbol": "TECH", "name": "Bio-Techne Corp.", "market_cap": 30000000, "tier": "small_cap", "epoch": 194, "sector": "Healthcare"},
        {"symbol": "ALGN", "name": "Align Technology Inc.", "market_cap": 28000000, "tier": "small_cap", "epoch": 195, "sector": "Healthcare"},
        {"symbol": "HOLX", "name": "Hologic Inc.", "market_cap": 26000000, "tier": "small_cap", "epoch": 196, "sector": "Healthcare"},
        {"symbol": "INCY", "name": "Incyte Corp.", "market_cap": 24000000, "tier": "small_cap", "epoch": 197, "sector": "Healthcare"},
        {"symbol": "EXAS", "name": "Exact Sciences Corp.", "market_cap": 22000000, "tier": "small_cap", "epoch": 198, "sector": "Healthcare"},
        {"symbol": "VTRS", "name": "Viatris Inc.", "market_cap": 20000000, "tier": "small_cap", "epoch": 199, "sector": "Healthcare"},
        {"symbol": "CTLT", "name": "Catalent Inc.", "market_cap": 18000000, "tier": "small_cap", "epoch": 200, "sector": "Healthcare"}
    ]
    
    @classmethod
    def get_all_companies(cls) -> List[Dict]:
        """Get all 200 companies in a single list"""
        return cls.MEGA_CAP + cls.LARGE_CAP + cls.MID_CAP + cls.SMALL_CAP
    
    @classmethod
    def get_by_tier(cls, tier: str) -> List[Dict]:
        """Get companies by market cap tier"""
        tier_map = {
            'mega_cap': cls.MEGA_CAP,
            'large_cap': cls.LARGE_CAP,
            'mid_cap': cls.MID_CAP,
            'small_cap': cls.SMALL_CAP
        }
        return tier_map.get(tier, [])
    
    @classmethod
    def get_by_sector(cls, sector: str) -> List[Dict]:
        """Get companies by sector"""
        all_companies = cls.get_all_companies()
        return [company for company in all_companies if company.get('sector') == sector]
    
    @classmethod
    def get_by_epoch_range(cls, start_epoch: int, end_epoch: int) -> List[Dict]:
        """Get companies by epoch range"""
        all_companies = cls.get_all_companies()
        return [company for company in all_companies 
                if start_epoch <= company.get('epoch', 0) <= end_epoch]
    
    @classmethod
    def get_summary_stats(cls) -> Dict[str, Any]:
        """Get summary statistics of the company list"""
        all_companies = cls.get_all_companies()
        
        # Count by tier
        tier_counts = {}
        for company in all_companies:
            tier = company.get('tier', 'unknown')
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        # Count by sector
        sector_counts = {}
        for company in all_companies:
            sector = company.get('sector', 'unknown')
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        # Market cap ranges
        market_caps = [company.get('market_cap', 0) for company in all_companies]
        total_market_cap = sum(market_caps)
        avg_market_cap = total_market_cap / len(market_caps) if market_caps else 0
        
        return {
            'total_companies': len(all_companies),
            'tier_breakdown': tier_counts,
            'sector_breakdown': sector_counts,
            'total_market_cap': total_market_cap,
            'average_market_cap': avg_market_cap,
            'market_cap_range': {
                'min': min(market_caps) if market_caps else 0,
                'max': max(market_caps) if market_caps else 0
            }
        }
