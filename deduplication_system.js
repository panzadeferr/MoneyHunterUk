/**
 * ROBUST DE-DUPLICATION SYSTEM FOR MONEY HUNTERS UK
 * 
 * This system protects manual referrals by preventing scraped offers
 * from overwriting or duplicating manually curated offers.
 * 
 * Key features:
 * 1. Manual offer protection - scraped offers that match manual store names are filtered out
 * 2. Multi-level matching - checks store names, URLs, and reward amounts
 * 3. Priority preservation - manual offers always take precedence
 * 4. Clear logging - shows what was removed and why
 * 5. Category normalization - ensures consistent categorization
 */

class DeduplicationSystem {
  constructor(existingOffers = []) {
    this.existingOffers = existingOffers;
    this.manualOffers = this.extractManualOffers();
    this.removedOffers = [];
    this.addedOffers = [];
  }

  /**
   * Extract manual offers from existing offers
   * Manual offers are those not starting with 'sc_' (Scrimpr) or containing 'scraped'
   */
  extractManualOffers() {
    return this.existingOffers.filter(offer => {
      const isManual = !offer.id.startsWith('sc_') && 
                      !offer.id.includes('scraped') &&
                      !offer.badge?.includes('MEGALIST') &&
                      !offer.badge?.includes('REDDIT FIND');
      return isManual;
    });
  }

  /**
   * Create a deduplication index for fast lookups
   */
  createDeduplicationIndex() {
    const index = {
      storeNames: new Set(),
      urls: new Set(),
      rewardPatterns: new Set()
    };

    this.manualOffers.forEach(offer => {
      // Store name (case-insensitive, trimmed)
      const storeName = offer.name.toLowerCase().trim();
      index.storeNames.add(storeName);

      // URL (if exists)
      if (offer.url && offer.url !== '#') {
        const cleanUrl = this.normalizeUrl(offer.url);
        if (cleanUrl) index.urls.add(cleanUrl);
      }

      // Reward pattern (extract numeric value)
      const rewardValue = this.extractRewardValue(offer.reward);
      if (rewardValue > 0) {
        index.rewardPatterns.add(`${storeName}-${rewardValue}`);
      }
    });

    return index;
  }

  /**
   * Normalize URL for comparison
   */
  normalizeUrl(url) {
    try {
      const urlObj = new URL(url);
      // Remove query parameters and fragments for comparison
      return `${urlObj.hostname}${urlObj.pathname}`.toLowerCase();
    } catch (e) {
      return url.toLowerCase();
    }
  }

  /**
   * Extract numeric value from reward string
   */
  extractRewardValue(reward) {
    const nums = String(reward).match(/\d+(\.\d+)?/g);
    if (!nums || !nums.length) return 0;
    return Math.max(...nums.map(Number));
  }

  /**
   * Check if a scraped offer is a duplicate of a manual offer
   */
  isDuplicate(scrapedOffer, dedupIndex) {
    const scrapedStoreName = scrapedOffer.name.toLowerCase().trim();
    
    // 1. Check exact store name match
    if (dedupIndex.storeNames.has(scrapedStoreName)) {
      return { isDuplicate: true, reason: `Exact store name match: "${scrapedOffer.name}"` };
    }

    // 2. Check partial store name match (e.g., "Chase UK" vs "Chase")
    for (const manualStoreName of dedupIndex.storeNames) {
      if (scrapedStoreName.includes(manualStoreName) || manualStoreName.includes(scrapedStoreName)) {
        return { isDuplicate: true, reason: `Partial store name match: "${scrapedOffer.name}" vs "${manualStoreName}"` };
      }
    }

    // 3. Check URL match (if scraped offer has a URL)
    if (scrapedOffer.url && scrapedOffer.url !== '#') {
      const scrapedUrl = this.normalizeUrl(scrapedOffer.url);
      if (dedupIndex.urls.has(scrapedUrl)) {
        return { isDuplicate: true, reason: `URL match: "${scrapedOffer.url}"` };
      }
    }

    // 4. Check reward pattern match
    const scrapedRewardValue = this.extractRewardValue(scrapedOffer.reward);
    if (scrapedRewardValue > 0) {
      const rewardPattern = `${scrapedStoreName}-${scrapedRewardValue}`;
      if (dedupIndex.rewardPatterns.has(rewardPattern)) {
        return { isDuplicate: true, reason: `Reward pattern match: "${scrapedOffer.name}" for ${scrapedRewardValue}` };
      }
    }

    return { isDuplicate: false, reason: '' };
  }

  /**
   * Normalize category for imported offers
   */
  normalizeCategory(rawCategory, rawType) {
    const value = String(rawCategory || rawType || '').toLowerCase();
    
    const categoryMap = {
      'bank_switch': 'bank',
      'bank': 'bank',
      'investment': 'invest',
      'invest': 'invest',
      'utilities': 'travel',
      'travel': 'travel',
      'freebies': 'freebie',
      'other': 'freebie',
      'cashback': 'cashback',
      'gift': 'gift',
      'business': 'business',
      'earn': 'earn',
      'mobile': 'mobile',
      'supermarket': 'freebie' // Supermarkets filtered out earlier
    };

    return categoryMap[value] || 'freebie';
  }

  /**
   * Process scraped offers and filter out duplicates
   */
  processScrapedOffers(scrapedData) {
    const dedupIndex = this.createDeduplicationIndex();
    const filteredOffers = [];
    
    console.log(`🔍 Starting de-duplication with ${scrapedData.length} scraped offers`);
    console.log(`📊 Manual offers to protect: ${this.manualOffers.length}`);
    console.log('📋 Manual store names:', Array.from(dedupIndex.storeNames));

    scrapedData.forEach((scraped, index) => {
      const duplicateCheck = this.isDuplicate(scraped, dedupIndex);
      
      if (duplicateCheck.isDuplicate) {
        this.removedOffers.push({
          scrapedOffer: scraped,
          reason: duplicateCheck.reason
        });
        console.log(`❌ Removed duplicate: ${scraped.name} - ${duplicateCheck.reason}`);
      } else {
        filteredOffers.push(scraped);
        console.log(`✅ Kept unique: ${scraped.name}`);
      }
    });

    console.log(`📊 Results: ${filteredOffers.length} kept, ${this.removedOffers.length} removed`);
    
    return filteredOffers;
  }

  /**
   * Map scraped data to offer format
   */
  mapToOfferFormat(scrapedData) {
    return scrapedData.map(d => {
      const type = String(d.type || '').toLowerCase();
      const idSeed = `${d.store || 'offer'}-${d.item || ''}-${d.deal_price || ''}`;
      
      // Use existing ID if it starts with 'sc_' (Scrimpr deals), otherwise generate one
      let id;
      if (d.id && d.id.startsWith('sc_')) {
        id = d.id; // Keep Scrimpr IDs as-is
      } else {
        id = idSeed
          .toLowerCase()
          .replace(/\s+/g, '-')
          .replace(/[^a-z0-9-]/g, '')
          .slice(0, 70) + '-scraped';
      }
      
      return {
        id: id,
        name: (d.store || 'New Offer').slice(0, 40),
        category: this.normalizeCategory(d.category, d.type),
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
      };
    });
  }

  /**
   * Get summary of de-duplication results
   */
  getSummary() {
    return {
      totalScraped: this.removedOffers.length + this.addedOffers.length,
      removed: this.removedOffers.length,
      added: this.addedOffers.length,
      removedDetails: this.removedOffers.map(r => ({
        name: r.scrapedOffer.name,
        reason: r.reason
      }))
    };
  }
}

/**
 * Enhanced loadOffersFromJSON function with robust de-duplication
 */
async function loadOffersFromJSONEnhanced(existingOffers) {
  try {
    console.log('🔄 Loading offers from JSON with enhanced de-duplication...');
    
    const res = await fetch('https://moneyhunters.co.uk/all_deals.json?v=' + Date.now());
    if (!res.ok) throw new Error('fetch failed');

    const data = await res.json();
    if (!data.deals || !data.deals.length) throw new Error('no deals');

    // Filter out supermarkets
    const supermarkets = ['tesco','asda','sainsbury','iceland','morrisons','waitrose','aldi','lidl'];
    const scraped = data.deals.filter(d => {
      const s = (d.store || '').toLowerCase();
      const t = (d.type || '').toLowerCase();

      // Remove supermarkets
      if (supermarkets.some(x => s.includes(x))) return false;

      // Keep only scraped offers
      const keep = t === 'scraped_reddit' || t === 'scraped_mse' || t === 'scraped_megalist';
      return keep;
    });

    console.log(`📥 Found ${scraped.length} scraped offers (after supermarket filter)`);

    if (!scraped.length) {
      console.log('📭 No scraped offers to process');
      return [];
    }

    // Initialize de-duplication system
    const dedupSystem = new DeduplicationSystem(existingOffers);
    
    // Process scraped offers
    const uniqueScraped = dedupSystem.processScrapedOffers(scraped);
    
    // Map to offer format
    const mappedOffers = dedupSystem.mapToOfferFormat(uniqueScraped);
    
    // Filter out offers that already exist by ID
    const existingIds = new Set(existingOffers.map(o => o.id));
    const newOffers = mappedOffers.filter(o => !existingIds.has(o.id));
    
    // Update added offers
    dedupSystem.addedOffers = newOffers;
    
    // Log summary
    const summary = dedupSystem.getSummary();
    console.log('📊 De-duplication Summary:', summary);
    
    if (summary.removed > 0) {
      console.log('🗑️ Removed offers:');
      summary.removedDetails.forEach(detail => {
        console.log(`   - ${detail.name}: ${detail.reason}`);
      });
    }
    
    console.log(`🎉 Successfully loaded ${newOffers.length} new unique offers`);
    
    return newOffers;
    
  } catch(e) {
    console.error('❌ Error loading JSON offers:', e.message);
    return [];
  }
}

// Export for use in app.html
if (typeof window !== 'undefined') {
  window.DeduplicationSystem = DeduplicationSystem;
  window.loadOffersFromJSONEnhanced = loadOffersFromJSONEnhanced;
}