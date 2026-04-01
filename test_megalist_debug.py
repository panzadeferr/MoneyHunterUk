import re
import requests
from datetime import datetime

def test_megalist_parsing():
    headers = {
        "User-Agent": "MoneyHuntersUK/1.0 (contact: hello@moneyhunters.co.uk)"
    }
    megalist_url = (
        "https://www.reddit.com/r/beermoneyuk/comments/"
        "1rywry0/the_beermoney_megalist_march_2026_"
        "the_big_list_of/.json"
    )
    
    try:
        r = requests.get(megalist_url, headers=headers, timeout=15)
        print(f"Megalist status: {r.status_code}")
        if r.status_code != 200:
            return []
        data = r.json()
        post = data[0]["data"]["children"][0]["data"]
        body = post.get("selftext", "")
        lines = body.split("\n")
        
        print(f"Total lines: {len(lines)}")
        
        # Test the new parsing logic
        deals = []
        for i, line in enumerate(lines[:50]):  # Check first 50 lines
            line = line.strip()
            if not line:
                continue
                
            print(f"\nLine {i}: '{line}'")
            
            # Skip long lines (descriptions, not offers)
            if len(line) > 100:
                print(f"  Skipped: line too long ({len(line)} chars)")
                continue
            
            # Must contain £ with a number
            if '£' not in line:
                print(f"  Skipped: no £ symbol")
                continue
            
            amounts = re.findall(r'£(\d+(?:\.\d{2})?)', line)
            if not amounts:
                print(f"  Skipped: no valid £ amount found")
                continue
            
            amount = float(amounts[0])
            if amount < 5 or amount > 800:
                print(f"  Skipped: amount {amount} outside range 5-800")
                continue
            
            # Clean markdown from line
            clean = re.sub(
                r'\[([^\]]+)\]\([^\)]+\)',  # [text](url) -> text
                r'\1', line
            )
            clean = re.sub(r'[*#>\-•|]', ' ', clean)
            clean = re.sub(r'https?://\S+', '', clean)
            clean = re.sub(r'£[\d,.]+', '', clean)
            clean = re.sub(r'\s+', ' ', clean).strip()
            
            print(f"  Cleaned: '{clean}'")
            
            # Extract store name - first 1-3 meaningful words
            words = [w for w in clean.split() 
                     if len(w) > 1 
                     and w.lower() not in [
                        'get','for','the','and','with',
                        'new','via','use','your','you',
                        'when','bonus','free','sign','up',
                        'open','spend','earn','refer','or',
                        'to','a','an','in','on','of','is',
                        'its','that','this','has','have',
                        'after','then','within','must','by',
                        'switching','signing','joining',
                        'depositing','making','completing',
                     ]]
            
            print(f"  Words after filtering: {words}")
            
            if not words:
                print(f"  Skipped: no meaningful words after filtering")
                continue
            
            # Store name = first word only if it looks 
            # like a brand (capitalised or known brand)
            store = words[0]
            
            # Must look like a proper brand name
            # Not a common English word
            if store.lower() in [
                'get','bonus','free','switch','bank',
                'invest','cashback','refer','sign','open',
                'deposit','spend','earn','complete','make',
                'join','apply','transfer','upgrade','use',
                'claim','register','create','activate',
            ]:
                # Try second word
                if len(words) > 1:
                    store = words[1]
                    print(f"  Using second word as store: {store}")
                else:
                    print(f"  Skipped: store '{store}' is common word, no second word")
                    continue
            
            # Store name sanity checks
            if len(store) < 2:
                print(f"  Skipped: store name too short")
                continue
            if store.isnumeric():
                print(f"  Skipped: store is numeric")
                continue
            # Must start with capital letter (brand name)
            if not store[0].isupper():
                print(f"  Skipped: store '{store}' doesn't start with capital letter")
                continue
            
            print(f"  ✓ Would add deal with store: {store}")
            
        return deals
        
    except Exception as e:
        print(f"Megalist failed: {e}")
        return []

if __name__ == "__main__":
    test_megalist_parsing()