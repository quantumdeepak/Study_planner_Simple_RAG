import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

class ChatHandler:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = None
        self.current_topic = None
        self.context = None
        self.question_count = 0
        self.max_questions = 5
        
    def start_chat(self, topic, context):
        """Initialize a new chat session"""
        self.current_topic = topic
        self.context = context
        self.chat = self.model.start_chat(history=[])
        self.question_count = 0
        
        system_prompt = f"""You are an expert and enthusiastic tutor teaching students about {topic}. 
        Use this context for accurate information: {context[:2000]}

        Act as a supportive educator who:
        1. Explains concepts clearly and builds on student understanding
        2. Responds warmly to confusion or uncertainty
        3. Provides detailed, constructive feedback
        4. Offers examples and analogies to clarify points
        5. Encourages critical thinking

        When starting the session, introduce yourself warmly and ask an engaging first question.

        When responding to student answers:
        - If they show understanding: Acknowledge it and build upon it
        - If they show partial understanding: Point out what's correct and gently clarify misconceptions
        - If they express confusion: Be encouraging and break down the concept into simpler parts
        - If they say "I don't know": Provide a helpful explanation and guide them to understanding

        Always format your responses clearly:

        For correct answers:
        "That's great! [Specific praise about their answer]
        
        You're right that [restate correct elements].
        
        Let's build on this:
        [Additional insight or connection]
        
        NEXT QUESTION:
        [Related but more challenging question]"

        For partially correct answers:
        "Good start! [Praise specific correct elements]
        
        You're right about [correct part]. Let's clarify something:
        [Clear explanation of misunderstood part]
        
        ADDITIONAL INFO:
        [Helpful context or examples]
        
        NEXT QUESTION:
        [Question that helps reinforce correct understanding]"

        For incorrect answers or confusion:
        "I appreciate you trying! Let's work through this together.
        
        EXPLANATION:
        [Clear, step-by-step explanation]
        
        EXAMPLE:
        [Concrete example or analogy]
        
        Let's try a simpler question:
        [More basic question about the same concept]"

        For "I don't know" responses:
        "That's okay! Learning new concepts takes time. Let me help explain:
        
        KEY CONCEPT:
        [Simple explanation]
        
        EXAMPLE:
        [Relatable example]
        
        Now, let's try an easier question:
        [Simpler version of the concept]"

        Keep your tone encouraging and focus on building understanding step by step."""
        
        # Generate welcoming first message
        welcome_prompt = f"""Create a welcoming first message that:
        1. Introduces you as an expert tutor
        2. Shows enthusiasm for teaching {topic}
        3. Asks an engaging but accessible first question
        4. Encourages the student to give their best try

        Use this format:
        "Hi! I'm your tutor for {topic}. [Engaging introduction]

        FIRST QUESTION:
        [Clear, approachable question]

        Don't worry if you're not sure - we'll learn together!"
        """
        
        response = self.chat.send_message(welcome_prompt)
        return response.text
    
    def handle_message(self, user_message):
        """Process user message and generate response"""
        if not self.chat:
            return "Chat session not initialized. Please start a new chat."
            
        # Check for conversation end
        if re.search(r'thanks?\s*bye|goodbye|bye\s*bye', user_message.lower()):
            return self._generate_final_feedback()
        
        self.question_count += 1
        if self.question_count >= self.max_questions:
            return self._generate_final_feedback()
            
        # Generate response based on user's message
        prompt = f"""The student responded: "{user_message}"

        Analyze their response and provide:
        1. Understanding level (full, partial, confused, or unsure)
        2. Specific feedback addressing their actual response
        3. Additional explanation if needed
        4. An appropriate follow-up question

        Remember:
        - Be encouraging but honest
        - Address specific content in their response
        - Provide examples when explaining concepts
        - Make connections to previous learning
        - Ask questions that build on their current understanding

        Choose and use the appropriate response format from your training."""
        
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._generate_fallback_response()
            
    def _generate_final_feedback(self):
        """Generate concluding feedback and end the session"""
        prompt = """Create a supportive final message that:
        1. Highlights specific concepts discussed
        2. Acknowledges their effort and participation
        3. Encourages continued learning
        4. Ends with concrete next steps

        Format:
        "Thank you for our study session! 

        KEY TAKEAWAYS:
        [List main concepts covered]

        PROGRESS HIGHLIGHTS:
        [Mention specific areas of improvement]

        NEXT STEPS:
        [Suggest ways to continue learning]

        Keep up the great work! 🎓"
        """
        
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return "Thank you for our study session! You've engaged well with the material and shown good progress. Keep exploring these concepts and don't hesitate to revisit them. Great work! 🎓"
    
    def _generate_fallback_response(self):
        """Generate a fallback response if main response fails"""
        return """I see you're thinking about this concept. Let's break it down together:

EXPLANATION:
[Brief explanation of the concept]

EXAMPLE:
[Simple example to illustrate]

Let's try approaching this from a different angle:
[Alternative question about the same concept]"""