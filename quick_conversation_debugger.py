#!/usr/bin/env python3
"""
Quick Conversation Debugger
Interactive testing interface for debugging conversation flows
"""

import sys
import os
import asyncio
sys.path.append('./thesis-agents')

from state_manager import ArchMentorState, StudentProfile
from orchestration.langgraph_orchestrator import LangGraphOrchestrator

class QuickConversationDebugger:
    def __init__(self):
        self.orchestrator = None
        self.state = None
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the orchestrator and state"""
        print("🔧 Initializing system...")
        try:
            self.orchestrator = LangGraphOrchestrator("architecture")
            
            # Create initial state
            self.state = ArchMentorState()
            self.state.current_design_brief = "I want to design a community center"
            self.state.student_profile = StudentProfile(skill_level="intermediate")
            self.state.domain = "architecture"
            
            print("✅ System initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return False
        return True
    
    def show_menu(self):
        """Show the main menu"""
        print("\n" + "="*60)
        print("🔍 QUICK CONVERSATION DEBUGGER")
        print("="*60)
        print("Choose an option:")
        print("1. Interactive conversation testing")
        print("2. Run sample questions")
        print("3. Custom conversation testing")
        print("4. Test your specific conversation")
        print("5. Show current state")
        print("6. Clear conversation history")
        print("7. Help")
        print("0. Exit")
        print("="*60)
    
    def show_help(self):
        """Show help information"""
        print("\n📖 HELP - Available Commands:")
        print("• Type your message normally to send it")
        print("• 'help' - Show this help")
        print("• 'state' - Show current conversation state")
        print("• 'clear' - Clear conversation history")
        print("• 'quit' - Exit the session")
        print("• 'routing' - Show routing information")
        print("• 'metrics' - Show response metrics")
        print("\n💡 Tips:")
        print("• Test different types of questions to see routing variety")
        print("• Try follow-up questions to test context understanding")
        print("• Ask for examples to test web search functionality")
    
    async def interactive_mode(self):
        """Interactive conversation mode"""
        print("\n🎯 Interactive Mode - Type your messages (type 'help' for commands)")
        print("Starting conversation...")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'state':
                    self.show_state()
                    continue
                elif user_input.lower() == 'clear':
                    self.clear_conversation()
                    continue
                elif user_input.lower() == 'routing':
                    self.show_routing_info()
                    continue
                elif user_input.lower() == 'metrics':
                    self.show_metrics()
                    continue
                
                # Process the message
                print("🤖 Processing...")
                result = await self.process_message(user_input)
                
                if result:
                    print(f"🤖 Assistant: {result['response']}")
                    print(f"🛤️  Routing: {result.get('routing_path', 'unknown')}")
                    print(f"📊 Type: {result.get('metadata', {}).get('response_type', 'unknown')}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def sample_questions_mode(self):
        """Run predefined sample questions"""
        sample_questions = [
            "What is adaptive reuse?",
            "How do I design flexible spaces for a community center?",
            "Can you provide examples of sustainable community centers?",
            "I'm confused about lighting design - can you help?",
            "What are the key principles of inclusive design?"
        ]
        
        print(f"\n📝 Running {len(sample_questions)} sample questions...")
        
        for i, question in enumerate(sample_questions, 1):
            print(f"\n{'='*60}")
            print(f"🎯 Question {i}: {question}")
            print(f"{'='*60}")
            
            result = await self.process_message(question)
            
            if result:
                print(f"🤖 Response: {result['response']}")
                print(f"🛤️  Routing: {result.get('routing_path', 'unknown')}")
                print(f"📊 Type: {result.get('metadata', {}).get('response_type', 'unknown')}")
            
            # Small delay between questions
            await asyncio.sleep(1)
        
        print(f"\n✅ Completed {len(sample_questions)} sample questions")
    
    async def custom_conversation_mode(self):
        """Custom conversation testing"""
        print("\n📝 Custom Conversation Mode")
        print("Enter your conversation messages (one per line)")
        print("Type 'done' when finished, or 'quit' to exit")
        
        messages = []
        while True:
            message = input("📝 Message: ").strip()
            
            if message.lower() == 'quit':
                return
            elif message.lower() == 'done':
                break
            elif message:
                messages.append(message)
        
        if messages:
            print(f"\n🔄 Running {len(messages)} messages...")
            for i, message in enumerate(messages, 1):
                print(f"\n--- Message {i} ---")
                result = await self.process_message(message)
                if result:
                    print(f"🤖 Response: {result['response']}")
    
    async def test_specific_conversation(self):
        """Test the specific conversation from your example"""
        conversation = [
            "I am curious about adaptive reuse principles that I can apply to my project",
            "It's going to be the neighborhood's main gathering spot — a place where people can meet, take classes, attend cultural events, play sports, and access community services all under one roof. We've got a really mixed crowd — families, seniors, teenagers, new immigrants, and local creatives. They'll need flexible spaces for meetings, classes, performances, sports, and just casual hanging out. Some will need quiet study areas, others will want open social spaces. It should be the beating heart of the neighborhood — a safe, welcoming space that brings people together and reflects the area's cultural diversity. I like that it keeps the character of the old building, cuts down on waste, and usually has a lot more personality than starting from scratch. Plus, it's a challenge — figuring out how to work with what's there while making it functional and inviting for modern use.",
            "So yeah, in my view, the core idea is flexibility with boundaries. You want people to feel like they can move around and make the space their own, but not end up with noise or chaos that ruins the experience for others. It's about letting the space breathe, keeping things intuitive, and using materials and layout to guide behavior without needing to put up signs everywhere. Now here's where I could use a bit of guidance: I'm trying to figure out the best way to approach lighting in a space like this. Daylight is a huge opportunity in a warehouse — big roof spans, high windows — but it can also create glare or uneven lighting if I'm not careful. How would you approach natural vs. artificial lighting in a reused warehouse space like this? Especially when it needs to work for all kinds of activities, from quiet study to sports to evening events?"
        ]
        
        print(f"\n🎯 Testing your specific conversation ({len(conversation)} messages)...")
        
        for i, message in enumerate(conversation, 1):
            print(f"\n{'='*60}")
            print(f"🎯 Message {i}: {message[:50]}...")
            print(f"{'='*60}")
            
            result = await self.process_message(message)
            
            if result:
                print(f"🤖 Response: {result['response']}")
                print(f"🛤️  Routing: {result.get('routing_path', 'unknown')}")
                print(f"📊 Type: {result.get('metadata', {}).get('response_type', 'unknown')}")
            
            await asyncio.sleep(1)
        
        print(f"\n✅ Completed your specific conversation test")
    
    async def process_message(self, user_input):
        """Process a single message through the orchestrator"""
        try:
            # Add user message to state
            self.state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Process through orchestrator
            result = await self.orchestrator.process_student_input(self.state)
            
            # Add assistant response to state
            self.state.messages.append({
                "role": "assistant",
                "content": result["response"]
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return None
    
    def show_state(self):
        """Show current conversation state"""
        print(f"\n📊 Current State:")
        print(f"• Messages: {len(self.state.messages)}")
        print(f"• Design Brief: {self.state.current_design_brief}")
        print(f"• Student Level: {self.state.student_profile.skill_level}")
        
        if self.state.messages:
            print(f"\n📝 Recent Messages:")
            for i, msg in enumerate(self.state.messages[-3:], 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:50] + "..." if len(msg.get('content', '')) > 50 else msg.get('content', '')
                print(f"  {i}. [{role}]: {content}")
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.state.messages = []
        print("🗑️  Conversation history cleared")
    
    def show_routing_info(self):
        """Show routing information"""
        print(f"\n🛤️  Routing Information:")
        print(f"• Last routing path: {getattr(self, 'last_routing_path', 'None')}")
        print(f"• Last response type: {getattr(self, 'last_response_type', 'None')}")
    
    def show_metrics(self):
        """Show response metrics"""
        print(f"\n📈 Response Metrics:")
        print(f"• Total messages: {len(self.state.messages)}")
        print(f"• User messages: {len([m for m in self.state.messages if m.get('role') == 'user'])}")
        print(f"• Assistant messages: {len([m for m in self.state.messages if m.get('role') == 'assistant'])}")
    
    async def run(self):
        """Main run loop"""
        if not self.initialize_system():
            return
        
        while True:
            self.show_menu()
            
            try:
                choice = input("Enter your choice (0-7): ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    await self.interactive_mode()
                elif choice == '2':
                    await self.sample_questions_mode()
                elif choice == '3':
                    await self.custom_conversation_mode()
                elif choice == '4':
                    await self.test_specific_conversation()
                elif choice == '5':
                    self.show_state()
                elif choice == '6':
                    self.clear_conversation()
                elif choice == '7':
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter 0-7.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function"""
    debugger = QuickConversationDebugger()
    await debugger.run()

if __name__ == "__main__":
    asyncio.run(main()) 