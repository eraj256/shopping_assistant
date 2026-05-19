import os
import json
from dotenv import load_dotenv
 
load_dotenv()
 
try:
    from groq import Groq
except ImportError:
    raise ImportError("pip install groq")
 
 
import os
import json
from groq import Groq
 
 
class ProfessionalChatbot:
    """PROFESSIONAL Chatbot - CartScout Optimized"""
    
    def __init__(self, products_data):
        # API Key environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing! Please set it in your environment.")
        
        self.client = Groq(api_key=api_key)
        self.products = products_data
        self.conversation = []
        self.build_index()
        self.categories_list = list(set([p['category'] for p in products_data]))
        
        # Define greetings ONCE at init
        self.greetings = ['hi', 'hello', 'hey', 'salam', 'aoa', 'how are you', 'kaise ho', 'hy']
        self.forbidden_topics = ['politics', 'election', 'war', 'news', 'prime minister', 'president', 'religion', 'ipl', 'cricket', 'weather']
    
    def build_index(self):
        self.product_index = {}
        for p in self.products:
            self.product_index[p['name'].lower()] = p
            self.product_index[p['brand'].lower()] = p
            if 'tags' in p:
                for tag in p['tags']:
                    self.product_index[tag.lower()] = p
    
    def find_product(self, query):
        q = query.lower().strip()
        # Direct lookup
        if q in self.product_index:
            return self.product_index[q]
        # Partial match
        for p in self.products:
            if q in p['name'].lower() or q in p['brand'].lower():
                return p
        return None
 
    def format_product(self, p):
        reviews = "\n".join([f"  • {r}" for r in p.get('reviews', [])[:2]])
        return f"""✅ **{p['name']}**
Brand: {p['brand']} | Price: ${p['price']:,.2f} | ⭐ {p['rating']}/5
Status: {'In Stock' if p['in_stock'] else 'Out of Stock'}
Advice: This product is highly popular due to its quality and the reliability of {p['brand']}.
Reviews:
{reviews}"""
 
    def chat(self, user_message):
        if not user_message.strip():
            return "Please type something!"
        u_msg = user_message.lower().strip()

        # IMPROVED: More robust greeting detection
        is_greeting = any(
            greet == u_msg or (greet in u_msg and len(u_msg) < 25)
            for greet in self.greetings
        )
        if is_greeting:
            greeting_response = (
                "Hello! I am your CartScout assistant. How can I help you find the perfect product today? "
                "I can give you advice on our Electronics and Fashion or anything else related to shopping!"
            )
            self.conversation.append({"role": "user", "content": user_message})
            self.conversation.append({"role": "assistant", "content": greeting_response})
            return greeting_response

        # FIX #2: Strict guardrail for forbidden topics
        if any(topic in u_msg for topic in self.forbidden_topics):
            forbidden_response = "Sorry!! You can only ask me about shopping or shopping-related things."
            self.conversation.append({"role": "user", "content": user_message})
            self.conversation.append({"role": "assistant", "content": forbidden_response})
            return forbidden_response

        # FIX #3: Product check
        product = self.find_product(u_msg)
        if product:
            response = self.format_product(product)
            self.conversation.append({"role": "user", "content": user_message})
            self.conversation.append({"role": "assistant", "content": response})
            return response

        # FIX #4: LLM logic with improved context
        system_instruction = f"""You are a professional Shopping Assistant for CartScout.
- Current Inventory Categories: {', '.join(self.categories_list)}.
- If user asks for advice or a product NOT in inventory, say: "Sorry, we don't have this product right now but we will work on this soon! Would you like to see our other products?"
- If they ask for general shopping advice (e.g., 'Which brand is better?'), provide a helpful comparison but keep it professional.
- NEVER talk about anything other than shopping. If they try to deviate, say: "I can only assist you with shopping related queries."
- Default Language: Always start in English.
- User Preference: If the user speaks in Roman Urdu (e.g., "kaise ho", "kya haal hai"), respond in Roman Urdu.
- Don't use Hindi words (i.e., vikalp)."""

        try:
            current_chat = [{"role": "user", "content": user_message}]
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": system_instruction}] + self.conversation + current_chat,
                max_tokens=150,
                temperature=0.5
            )

            response = completion.choices[0].message.content
            self.conversation.append({"role": "user", "content": user_message})
            self.conversation.append({"role": "assistant", "content": response})
            return response

        except Exception as e:
            error_response = (
                f"I'm sorry, I'm having trouble connecting. But generally, we deal in Electronics and Fashion. "
                f"Could you ask about those? (Error: {str(e)})"
            )
            print(f"[ERROR] {error_response}")
            return "I'm sorry, I'm having trouble connecting. But generally, we deal in Electronics and Fashion. Could you ask about those?"

    def reset(self):
        self.conversation = []