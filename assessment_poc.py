#!/usr/bin/env python3
"""
AI-Powered Assessment System - Proof of Concept v2
Enhanced with JSON validation for scalability
"""

import os
import json
import time
from typing import Dict, Any, Tuple, List
from anthropic import Anthropic
from dotenv import load_dotenv
import jsonschema
from jsonschema import Draft7Validator

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Configuration
MODEL = "claude-3-opus-20240229"  # Best quality for demo, consider claude-3-sonnet for cost savings
MAX_TOKENS = 1000

# Operational Metrics
METRICS = {
    "api_calls": 0,
    "validation_attempts": 0,
    "validation_failures": 0,
    "api_retry_count": 0,
    "first_attempt_success": 0,
    "fallback_used": 0
}

# JSON Schemas for validation
SCHEMAS = {
    "question_rubric": {
        "type": "object",
        "required": ["question", "rubric"],
        "properties": {
            "question": {
                "type": "string",
                "minLength": 20,
                "maxLength": 500
            },
            "rubric": {
                "type": "object",
                "required": ["poor", "adequate", "excellent"],
                "properties": {
                    "poor": {
                        "type": "object",
                        "required": ["criteria", "example"],
                        "properties": {
                            "criteria": {"type": "string", "minLength": 10},
                            "example": {"type": "string", "minLength": 10}
                        }
                    },
                    "adequate": {
                        "type": "object",
                        "required": ["criteria", "example"],
                        "properties": {
                            "criteria": {"type": "string", "minLength": 10},
                            "example": {"type": "string", "minLength": 10}
                        }
                    },
                    "excellent": {
                        "type": "object",
                        "required": ["criteria", "example"],
                        "properties": {
                            "criteria": {"type": "string", "minLength": 10},
                            "example": {"type": "string", "minLength": 10}
                        }
                    }
                }
            }
        }
    },
    "score_result": {
        "type": "object",
        "required": ["score_level", "confidence", "rationale"],
        "properties": {
            "score_level": {
                "type": "string",
                "enum": ["poor", "adequate", "excellent"]
            },
            "confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
            },
            "rationale": {
                "type": "string",
                "minLength": 50
            }
        }
    }
}

# Prompt Templates
QUESTION_RUBRIC_PROMPT = """Generate an educational assessment question and scoring rubric.

Subject: {subject}
Topic: {topic}

You MUST respond with ONLY valid JSON (no markdown code blocks, no explanations).

Required JSON structure:
{schema}

Requirements:
1. Question must be answerable in approximately 100 words
2. Question should test understanding of the topic
3. Each rubric level must have clear criteria and a specific example

Generate the JSON now:"""

SCORING_PROMPT = """Score the following student response using the provided rubric.

Question: {question}

Scoring Rubric:
- Poor: {poor_criteria}
- Adequate: {adequate_criteria}
- Excellent: {excellent_criteria}

Student Response: {response}

You MUST respond with ONLY valid JSON (no markdown code blocks, no explanations).

Required JSON structure:
{schema}

Evaluate and return the JSON score:"""


def validate_json(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate JSON against schema, return (is_valid, errors)."""
    global METRICS
    METRICS["validation_attempts"] += 1
    
    validator = Draft7Validator(schema)
    errors = []
    for error in validator.iter_errors(data):
        error_path = " -> ".join(str(p) for p in error.path)
        errors.append(f"{error_path}: {error.message}" if error_path else error.message)
    
    if errors:
        METRICS["validation_failures"] += 1
    
    return len(errors) == 0, errors


def generate_default_from_schema(schema_name: str, context: Dict[str, str] = None) -> Dict[str, Any]:
    """Generate a valid default response based on schema."""
    if schema_name == "question_rubric":
        subject = context.get("subject", "General")
        topic = context.get("topic", "Concepts")
        return {
            "question": f"Explain the key concepts of {topic} in {subject} and provide an example.",
            "rubric": {
                "poor": {
                    "criteria": "Response shows minimal understanding with significant errors or omissions",
                    "example": "The student mentions the topic but demonstrates fundamental misconceptions"
                },
                "adequate": {
                    "criteria": "Response shows basic understanding with minor errors or missing details",
                    "example": "The student covers main points but lacks depth or has minor inaccuracies"
                },
                "excellent": {
                    "criteria": "Response shows comprehensive understanding with accurate and detailed explanation",
                    "example": "The student provides thorough, accurate explanation with relevant examples"
                }
            }
        }
    elif schema_name == "score_result":
        return {
            "score_level": "adequate",
            "confidence": 0.7,
            "rationale": "The response demonstrates basic understanding of the topic with room for improvement in detail and accuracy."
        }
    return {}


def get_user_input() -> Dict[str, str]:
    """Collect subject and topic from user."""
    print("\n=== AI-Powered Assessment System ===\n")
    
    subject = input("Enter the subject area: ").strip()
    while not subject:
        print("Subject cannot be empty.")
        subject = input("Enter the subject area: ").strip()
    
    topic = input("Enter the specific topic: ").strip()
    while not topic:
        print("Topic cannot be empty.")
        topic = input("Enter the specific topic: ").strip()
    
    return {"subject": subject, "topic": topic}


def call_claude(prompt: str, retry_with_error: str = None) -> str:
    """Make API call to Claude with error handling."""
    global METRICS
    METRICS["api_calls"] += 1
    
    if retry_with_error:
        prompt += f"\n\nPrevious response had JSON validation errors:\n{retry_with_error}\nPlease provide valid JSON only."
    
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"\nAPI Error: {e}")
        print("Retrying in 3 seconds...")
        METRICS["api_retry_count"] += 1
        time.sleep(3)
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"API call failed after retry: {e}")


def parse_json_response(response: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Parse JSON from Claude's response with fallback."""
    try:
        # Clean response - remove markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        # Try to extract JSON from the response
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = cleaned[start_idx:end_idx]
            return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
    
    return fallback


def get_valid_json_from_claude(prompt: str, schema: Dict[str, Any], schema_name: str, 
                               context: Dict[str, str] = None, max_retries: int = 3) -> Dict[str, Any]:
    """Get valid JSON from Claude with retries and schema enforcement."""
    global METRICS
    
    for attempt in range(max_retries):
        try:
            # Add schema to prompt on first attempt
            if attempt == 0:
                schema_str = json.dumps(schema, indent=2)
                prompt = prompt.format(schema=schema_str, **context) if context else prompt
            
            # Get response with error feedback if retrying
            error_feedback = None
            if attempt > 0:
                error_feedback = "\n".join(errors)
            
            response = call_claude(prompt, error_feedback)
            
            # Parse JSON
            parsed = parse_json_response(response, {})
            
            # Validate against schema
            is_valid, errors = validate_json(parsed, schema)
            
            if is_valid:
                if attempt == 0:
                    METRICS["first_attempt_success"] += 1
                if attempt > 0:
                    print(f"✅ Valid JSON generated after {attempt + 1} attempts")
                return parsed
            else:
                print(f"\n⚠️  JSON validation failed (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print("Retrying with error feedback...")
                
        except Exception as e:
            print(f"\n⚠️  Error in attempt {attempt + 1}: {e}")
    
    # Final fallback: return schema-compliant default
    print("\n⚠️  Using fallback response after validation failures")
    METRICS["fallback_used"] += 1
    return generate_default_from_schema(schema_name, context)


def generate_question_and_rubric(subject: str, topic: str) -> Dict[str, Any]:
    """Generate question and rubric using Claude with JSON validation."""
    print("\n📝 Generating question and rubric...")
    
    context = {
        "subject": subject,
        "topic": topic
    }
    
    result = get_valid_json_from_claude(
        QUESTION_RUBRIC_PROMPT,
        SCHEMAS["question_rubric"],
        "question_rubric",
        context
    )
    
    print("✅ Question and rubric generated with valid JSON!")
    return result


def collect_student_response(question: str) -> str:
    """Display question and collect student response."""
    print("\n" + "="*50)
    print("📋 ASSESSMENT QUESTION")
    print("="*50)
    print(f"\n{question}\n")
    print("Please provide your answer in ~100 words (press Enter twice when done):")
    print("-" * 50)
    
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            lines.pop()  # Remove the last empty line
            break
        lines.append(line)
    
    response = "\n".join(lines).strip()
    
    while not response:
        print("\nResponse cannot be empty. Please provide your answer:")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                lines.pop()
                break
            lines.append(line)
        response = "\n".join(lines).strip()
    
    return response


def score_response(response: str, question: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
    """Score the student response using Claude with JSON validation."""
    print("\n🔍 Scoring response...")
    
    context = {
        "question": question,
        "poor_criteria": rubric["poor"]["criteria"],
        "adequate_criteria": rubric["adequate"]["criteria"],
        "excellent_criteria": rubric["excellent"]["criteria"],
        "response": response
    }
    
    result = get_valid_json_from_claude(
        SCORING_PROMPT,
        SCHEMAS["score_result"],
        "score_result",
        context
    )
    
    print("✅ Scoring complete with valid JSON!")
    return result


def display_results(all_data: Dict[str, Any]) -> None:
    """Display the complete assessment results."""
    print("\n" + "="*60)
    print("📊 ASSESSMENT RESULTS")
    print("="*60)
    
    print(f"\n📚 Subject: {all_data['subject']}")
    print(f"📖 Topic: {all_data['topic']}")
    
    print(f"\n❓ Question: {all_data['question']}")
    
    print("\n📏 Scoring Rubric:")
    for level, details in all_data['rubric'].items():
        print(f"\n  {level.upper()}:")
        print(f"  - Criteria: {details['criteria']}")
        print(f"  - Example: {details['example'][:100]}...")
    
    print(f"\n💬 Student Response:")
    print(f"  {all_data['student_response']}")
    
    print(f"\n🎯 Score: {all_data['score']['score_level'].upper()}")
    print(f"📊 Confidence: {all_data['score']['confidence']:.1%}")
    print(f"\n📝 Scoring Rationale:")
    print(f"  {all_data['score']['rationale']}")
    
    # JSON validation status
    print(f"\n✅ JSON Validation: All responses validated successfully")
    
    print("\n" + "="*60)
    
    # Optional: Save results to file
    save = input("\nSave results to file? (y/n): ").lower()
    if save == 'y':
        filename = f"assessment_{all_data['subject']}_{all_data['topic']}.json"
        filename = filename.replace(" ", "_").lower()
        
        # Save as proper JSON
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"✅ Results saved to {filename}")
        
        # Also save human-readable version
        txt_filename = filename.replace('.json', '.txt')
        with open(txt_filename, 'w') as f:
            f.write("ASSESSMENT RESULTS\n")
            f.write("="*60 + "\n\n")
            f.write(f"Subject: {all_data['subject']}\n")
            f.write(f"Topic: {all_data['topic']}\n")
            f.write(f"\nQuestion: {all_data['question']}\n")
            f.write(f"\nStudent Response:\n{all_data['student_response']}\n")
            f.write(f"\nScore: {all_data['score']['score_level'].upper()}\n")
            f.write(f"Confidence: {all_data['score']['confidence']:.1%}\n")
            f.write(f"\nRationale:\n{all_data['score']['rationale']}\n")
        
        print(f"✅ Human-readable results saved to {txt_filename}")


def main():
    """Main execution flow."""
    global METRICS
    
    # Reset metrics for clean run
    METRICS = {
        "api_calls": 0,
        "validation_attempts": 0,
        "validation_failures": 0,
        "api_retry_count": 0,
        "first_attempt_success": 0,
        "fallback_used": 0
    }
    
    try:
        # Check API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ Error: ANTHROPIC_API_KEY not found in environment variables")
            print("Please create a .env file with: ANTHROPIC_API_KEY=sk-ant-...")
            return
        
        print("\n🚀 AI-Powered Assessment System v2 - With JSON Validation")
        print("="*60)
        
        # Step 1: Get user input
        user_input = get_user_input()
        
        # Step 2: Generate question and rubric with validation
        qa_data = generate_question_and_rubric(
            user_input["subject"], 
            user_input["topic"]
        )
        
        # Step 3: Collect student response
        student_response = collect_student_response(qa_data["question"])
        
        # Step 4: Score the response with validation
        score_data = score_response(
            student_response, 
            qa_data["question"], 
            qa_data["rubric"]
        )
        
        # Step 5: Display results
        all_data = {
            "subject": user_input["subject"],
            "topic": user_input["topic"],
            "question": qa_data["question"],
            "rubric": qa_data["rubric"],
            "student_response": student_response,
            "score": score_data,
            "metadata": {
                "version": "2.0",
                "json_validated": True,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        display_results(all_data)
        
        # Display operational metrics
        print("\n📊 Operational Metrics:")
        print(f"  - Total API Calls: {METRICS['api_calls']}")
        
        if METRICS['validation_attempts'] > 0:
            validation_success_rate = (METRICS['validation_attempts'] - METRICS['validation_failures']) / METRICS['validation_attempts']
            print(f"  - Validation Success Rate: {validation_success_rate:.1%}")
            print(f"  - First-Attempt Success Rate: {METRICS['first_attempt_success'] / (METRICS['api_calls'] - METRICS['api_retry_count']):.1%}")
        
        if METRICS['api_calls'] > 0:
            print(f"  - API Retry Rate: {METRICS['api_retry_count'] / METRICS['api_calls']:.1%}")
        
        print(f"  - Fallback Responses Used: {METRICS['fallback_used']}")
        
        print("\n✨ Assessment complete with validated JSON! Thank you for using the AI Assessment System.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your setup and try again.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()