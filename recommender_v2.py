"""
SHOPPING ASSISTANT - RECOMMENDATION ENGINE v2
Advanced recommendations with multiple strategies
"""

import json
import pandas as pd
import numpy as np
from typing import List, Dict

class ShoppingAssistant:
    """AI Shopping Assistant with smart recommendations"""
    
    def __init__(self, json_path='products.json'):
        """Load products from JSON"""
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        self.products = self.data['products']
        self.metadata = self.data['metadata']
        self.df = pd.DataFrame(self.products)
        
        print(f"✅ Loaded {len(self.products)} products from {len(self.metadata['categories'])} categories")
    
    def get_categories(self):
        """Get all available categories"""
        return sorted(self.metadata['categories'])
    
    def get_brands(self):
        """Get all available brands"""
        return sorted(self.metadata['brands'])
    
    def recommend_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """
        Get top products in a category
        """
        products = [p for p in self.products if p['category'] == category]
        
        # Sort by rating (descending) then by review count
        products = sorted(products, 
                         key=lambda x: (x['rating'], x['review_count']), 
                         reverse=True)
        
        return products[:limit]
    
    def recommend_by_budget(self, max_price: float, limit: int = 5) -> List[Dict]:
        """
        Recommend products within budget
        Prioritizes high-rated products
        """
        products = [p for p in self.products if p['price'] <= max_price and p['in_stock']]
        
        # Sort by rating first
        products = sorted(products, 
                         key=lambda x: x['rating'], 
                         reverse=True)
        
        return products[:limit]
    
    def smart_recommend(self, 
                        category: str = None,
                        max_price: float = None,
                        min_rating: float = 3.0,
                        tags: List[str] = None,
                        limit: int = 5) -> List[Dict]:
        """
        SMART recommendation combining multiple factors
        Scoring: Rating (40%) + Price Value (30%) + Popularity (20%) + Tags (10%)
        """
        candidates = self.products.copy()
        
        # Filter by constraints
        if category:
            candidates = [p for p in candidates if p['category'] == category]
        
        if max_price:
            candidates = [p for p in candidates if p['price'] <= max_price]
        
        candidates = [p for p in candidates if p['rating'] >= min_rating and p['in_stock']]
        
        if not candidates:
            return []
        
        # Calculate scores
        for product in candidates:
            score = 0
            
            # Rating score (0-5 normalized to 0-40)
            score += (product['rating'] / 5.0) * 40
            
            # Price value score (cheaper = better, 0-30)
            max_price_in_results = max(p['price'] for p in candidates)
            price_ratio = 1 - (product['price'] / max_price_in_results)
            score += price_ratio * 30
            
            # Popularity score (review count, 0-20)
            max_reviews = max(p['review_count'] for p in candidates)
            popularity_ratio = product['review_count'] / max_reviews if max_reviews > 0 else 0
            score += popularity_ratio * 20
            
            # Tags matching (0-10)
            if tags:
                tag_matches = sum(1 for tag in tags if any(tag.lower() in pt.lower() for pt in product['tags']))
                tag_score = (tag_matches / len(tags)) * 10 if tag_matches > 0 else 0
                score += tag_score
            
            product['recommendation_score'] = score
        
        # Sort by score
        candidates = sorted(candidates, key=lambda x: x['recommendation_score'], reverse=True)
        
        return candidates[:limit]
    
    def find_similar(self, product_id: int, limit: int = 3) -> List[Dict]:
        """
        Find similar products based on:
        - Same category
        - Similar price range
        - Similar rating
        """
        target = next((p for p in self.products if p['id'] == product_id), None)
        if not target:
            return []
        
        similar = []
        for p in self.products:
            if p['id'] == product_id:
                continue
            
            # Same category is most important
            if p['category'] != target['category']:
                continue
            
            # Similar price (within 30%)
            price_diff = abs(p['price'] - target['price']) / target['price']
            if price_diff > 0.3:
                continue
            
            similar.append(p)
        
        # Sort by rating
        similar = sorted(similar, key=lambda x: x['rating'], reverse=True)
        return similar[:limit]
    
    def search_products(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search products by name, brand, or tags
        """
        query = query.lower()
        results = []
        
        for product in self.products:
            # Check name
            if query in product['name'].lower():
                results.append((product, 3))  # Priority 3
                continue
            
            # Check brand
            if query in product['brand'].lower():
                results.append((product, 2))  # Priority 2
                continue
            
            # Check tags
            if any(query in tag.lower() for tag in product['tags']):
                results.append((product, 1))  # Priority 1
        
        # Sort by priority then by rating
        results = sorted(results, key=lambda x: (x[1], x[0]['rating']), reverse=True)
        return [r[0] for r in results[:limit]]
    
    def get_category_stats(self, category: str) -> Dict:
        """Get statistics for a category"""
        cat_products = [p for p in self.products if p['category'] == category]
        
        if not cat_products:
            return {}
        
        return {
            "category": category,
            "total_products": len(cat_products),
            "avg_price": np.mean([p['price'] for p in cat_products]),
            "avg_rating": np.mean([p['rating'] for p in cat_products]),
            "brands": len(set(p['brand'] for p in cat_products)),
            "price_range": {
                "min": min(p['price'] for p in cat_products),
                "max": max(p['price'] for p in cat_products)
            }
        }
    
    def print_summary(self):
        """Print project summary"""
        print("\n" + "="*70)
        print("🛍️  SHOPPING ASSISTANT - LOADED DATA SUMMARY")
        print("="*70)
        print(f"\n📊 PRODUCTS:")
        print(f"   Total Products: {self.metadata['total_products']}")
        print(f"   Categories: {self.metadata['total_categories']}")
        print(f"   Brands: {self.metadata['total_brands']}")
        
        print(f"\n💰 PRICING:")
        print(f"   Min: ${self.metadata['price_range']['min']:.2f}")
        print(f"   Max: ${self.metadata['price_range']['max']:.2f}")
        print(f"   Avg: ${self.metadata['price_range']['avg']:.2f}")
        
        print(f"\n⭐ RATINGS:")
        print(f"   Min: {self.metadata['rating_range']['min']}")
        print(f"   Max: {self.metadata['rating_range']['max']}")
        print(f"   Avg: {self.metadata['rating_range']['avg']:.2f}")
        
        print(f"\n📂 CATEGORIES ({self.metadata['total_categories']}):")
        for cat in self.metadata['categories']:
            count = len([p for p in self.products if p['category'] == cat])
            print(f"   • {cat}: {count} products")
        
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Test the assistant
    assistant = ShoppingAssistant('products.json')
    
    # Print summary
    assistant.print_summary()
    
    # Test 1: Recommend by category
    print("TEST 1: Top Electronics")
    recs = assistant.recommend_by_category('Electronics', limit=3)
    for r in recs:
        print(f"  • {r['name']} - ${r['price']} - ⭐{r['rating']}")
    
    # Test 2: Budget recommendations
    print("\nTEST 2: Best products under $200")
    recs = assistant.recommend_by_budget(200, limit=3)
    for r in recs:
        print(f"  • {r['name']} - ${r['price']} - ⭐{r['rating']}")
    
    # Test 3: Smart recommendation
    print("\nTEST 3: Smart: Electronics, under $500, wireless")
    recs = assistant.smart_recommend(
        category='Electronics',
        max_price=500,
        tags=['wireless'],
        limit=3
    )
    for r in recs:
        print(f"  • {r['name']} - ${r['price']} - ⭐{r['rating']} (Score: {r['recommendation_score']:.1f})")
    
    # Test 4: Search
    print("\nTEST 4: Search 'apple'")
    recs = assistant.search_products('apple', limit=3)
    for r in recs:
        print(f"  • {r['name']} - ${r['price']}")
    
    # Test 5: Similar products
    print("\nTEST 5: Similar to AirPods Pro 2 (ID: 1)")
    recs = assistant.find_similar(1, limit=3)
    for r in recs:
        print(f"  • {r['name']} - ${r['price']} - ⭐{r['rating']}")
