with open('app.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Corruption starts at 169604 (the ' node -e' text)
# Good closing starts at 180035
corrupt_start = 169604
good_close_abs = 180035

# The clean loadOffersFromJSON function to insert
clean_function = '''
    async function loadOffersFromJSON() {
      try {
        const res = await fetch('https://moneyhunters.co.uk/all_deals.json?v=' + Date.now());
        if (!res.ok) throw new Error('fetch failed');

        const data = await res.json();
        if (!data.deals || !data.deals.length) throw new Error('no deals');

        const supermarkets = ['tesco','asda','sainsbury','iceland','morrisons','waitrose','aldi','lidl'];

        const scraped = data.deals.filter(d => {
          const s = (d.store || '').toLowerCase();
          const t = (d.type || '').toLowerCase();
          if (supermarkets.some(x => s.includes(x))) return false;
          return t === 'scraped_reddit' || t === 'scraped_mse' || t === 'scraped_megalist';
        });

        if (!scraped.length) return;

        const existingIds = new Set(offers.map(o => o.id));

        // Build a set of manual offer names (case-insensitive) for de-duplication
        // Manual offers are those whose IDs don't start with 'sc_'
        const manualStoreNames = new Set();
        offers.forEach(offer => {
          if (offer.id && !offer.id.startsWith('sc_')) {
            manualStoreNames.add(offer.name.toLowerCase().trim());
          }
        });

        console.log('[Safety Guard] Manual offers protected:', manualStoreNames.size);

        const normalizeImportedCategory = (raw) => {
          const value = String(raw || '').toLowerCase();
          if (value === 'bank_switch') return 'bank';
          if (value === 'investment') return 'invest';
          if (value === 'utilities') return 'travel';
          if (value === 'freebies' || value === 'other') return 'freebie';
          return ['bank','invest','cashback','gift','business','earn','mobile','travel','freebie','supermarket'].includes(value)
            ? value
            : 'freebie';
        };

        const mapped = scraped.map(d => {
          const type = String(d.type || '').toLowerCase();
          const idSeed = `${d.store || 'offer'}-${d.item || ''}-${d.deal_price || ''}`;

          let id;
          if (d.id && d.id.startsWith('sc_')) {
            id = d.id;
          } else {
            id = idSeed
              .toLowerCase()
              .replace(/\\s+/g, '-')
              .replace(/[^a-z0-9-]/g, '')
              .slice(0, 70) + '-scraped';
          }

          return ({
            id: id,
            name: (d.store || 'New Offer').slice(0, 40),
            category: normalizeImportedCategory(d.category || d.type),
            reward: d.deal_price || 'Bonus',
            amount: parseFloat(
              String(d.deal_price || '0')
                .replace(/[^0-9.]/g, '')
            ) || 0,
            badge: type === 'scraped_megalist' ? '📋 MEGALIST' : '🔍 REDDIT FIND',
            effort: 'Check source for details',
            desc: (d.item || d.store || d.desc || '').slice(0, 120),
            code: d.code || '',
            url: d.link || '#',
            steps: d.steps || [
              'Read offer details',
              'Follow link to claim'
            ],
            expectedDays: 30,
            tips: ['Always verify terms before claiming'],
            warnings: ['Details may change - check source'],
            detailedSteps: d.steps || []
          });
        });

        // Safety Guard: filter out scraped offers that duplicate manual offers
        const filteredMapped = mapped.filter(o => {
          const scrapedStoreName = o.name.toLowerCase().trim();
          const isDuplicate = manualStoreNames.has(scrapedStoreName);
          if (isDuplicate) {
            console.log(`[Safety Guard] Blocked duplicate: "${o.name}"`);
            return false;
          }
          return true;
        });

        const removedCount = mapped.length - filteredMapped.length;
        if (removedCount > 0) {
          console.log(`[Safety Guard] Removed ${removedCount} scraped offers that duplicate manual offers`);
        }

        const newOffers = filteredMapped.filter(o => !existingIds.has(o.id));

        if (newOffers.length) {
          offers.push(...newOffers);
          console.log('Loaded ' + newOffers.length + ' fresh offers from JSON (after de-duplication)');
        }
      } catch(e) {
        console.log('Error loading JSON offers, using hardcoded offers:', e.message);
      }
    }

'''

# Build the fixed content
before_corrupt = content[:corrupt_start]
after_corrupt = content[good_close_abs:]

fixed_content = before_corrupt + clean_function + after_corrupt

print('Original length:', len(content))
print('Fixed length:', len(fixed_content))
print('Corruption removed:', len(content) - len(fixed_content))

# Verify no conflict markers remain
import re
conflicts = re.findall(r'(<<<<<<< |>>>>>>> |^=======)', fixed_content, re.MULTILINE)
print('Remaining conflict markers:', conflicts)

# Write the fixed file
with open('app.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('File written successfully!')
