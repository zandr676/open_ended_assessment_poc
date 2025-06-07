# open_ended_assessment_poc
An LLM demo that generates a question and scores an answer

# AI-Powered Assessment System

An intelligent educational assessment tool that automatically generates questions, creates scoring rubrics, and evaluates student responses using Claude AI with robust JSON validation.

## Features

- **Dynamic Question Generation**: Creates custom assessment questions based on subject and topic
- **Automated Rubric Creation**: Generates comprehensive scoring criteria (Poor, Adequate, Excellent)
- **AI-Powered Scoring**: Evaluates student responses with confidence metrics and detailed rationale
- **JSON Schema Validation**: Ensures reliable, structured responses from AI
- **Error Recovery**: Automatic retry mechanisms and fallback responses
- **Results Export**: Save assessments in both JSON and human-readable formats
- **Operational Metrics**: Track API usage, validation success rates, and system performance

## Requirements

### Python Dependencies

```bash
pip install anthropic python-dotenv jsonschema
```

### API Access

- Anthropic API key (Claude AI access)
- Create account at [Anthropic Console](https://console.anthropic.com/)

## Installation

1. **Clone or download the script**
   ```bash
   # Save as assessment_poc.py
   ```

2. **Install dependencies**
   ```bash
   pip install anthropic python-dotenv jsonschema
   ```

3. **Set up environment variables**
   Create a `.env` file in the same directory:
   ```env
   ANTHROPIC_API_KEY=sk-ant-your-api-key-here
   ```

## Usage

### Basic Usage

```bash
python assessment_poc.py
```

The system will guide you through:

1. **Subject Input**: Enter the academic subject (e.g., "Biology", "Mathematics")
2. **Topic Input**: Specify the specific topic (e.g., "Photosynthesis", "Quadratic Equations")
3. **Question Display**: Review the generated assessment question
4. **Response Collection**: Provide your answer (press Enter twice when finished)
5. **Results Review**: View your score, confidence level, and detailed feedback

### Example Session

```
=== AI-Powered Assessment System ===

Enter the subject area: Biology
Enter the specific topic: Photosynthesis

📝 Generating question and rubric...
✅ Question and rubric generated with valid JSON!

==================================================
📋 ASSESSMENT QUESTION
==================================================

Explain the process of photosynthesis and its importance 
to life on Earth. Include the main reactants and products.

Please provide your answer in ~100 words (press Enter twice when done):
--------------------------------------------------
[Your response here]

🔍 Scoring response...
✅ Scoring complete with valid JSON!

📊 ASSESSMENT RESULTS
==================================================
🎯 Score: ADEQUATE
📊 Confidence: 75.0%
📝 Scoring Rationale: The response demonstrates good understanding...
```

## Configuration

### Model Settings

```python
MODEL = "claude-3-opus-20240229"  # High quality (expensive)
# MODEL = "claude-3-sonnet-20240229"  # Cost-effective alternative
MAX_TOKENS = 1000
```

### Validation Schema

The system uses JSON schemas to ensure structured responses:

- **Question/Rubric Schema**: Validates generated questions and scoring criteria
- **Score Result Schema**: Validates assessment outcomes with confidence metrics

### Retry Logic

- **Max Retries**: 3 attempts for JSON validation
- **API Retry**: Automatic retry with 3-second delay on failures
- **Fallback System**: Schema-compliant defaults when validation fails

## Output Formats

### Console Display
- Formatted assessment results with emojis and clear sections
- Real-time progress indicators
- Operational metrics summary

### File Export
- **JSON Format**: Machine-readable structured data
- **Text Format**: Human-readable assessment report
- **Automatic Naming**: `assessment_[subject]_[topic].json/txt`

### Sample JSON Output
```json
{
  "subject": "Biology",
  "topic": "Photosynthesis",
  "question": "Explain the process of photosynthesis...",
  "rubric": {
    "poor": {
      "criteria": "Response shows minimal understanding...",
      "example": "Student mentions light but lacks detail..."
    }
  },
  "student_response": "Photosynthesis is when plants...",
  "score": {
    "score_level": "adequate",
    "confidence": 0.75,
    "rationale": "The response demonstrates..."
  },
  "metadata": {
    "version": "2.0",
    "json_validated": true,
    "timestamp": "2025-06-06 14:30:22"
  }
}
```

## System Metrics

The system tracks operational performance:

- **API Call Count**: Total requests to Claude
- **Validation Success Rate**: JSON schema compliance percentage
- **First-Attempt Success Rate**: Responses valid without retry
- **API Retry Rate**: Network/service failure recovery
- **Fallback Usage**: Schema-default response frequency

## Error Handling

### Common Issues

1. **Missing API Key**
   ```
   ❌ Error: ANTHROPIC_API_KEY not found in environment variables
   ```
   **Solution**: Create `.env` file with valid API key

2. **Network Connectivity**
   ```
   API Error: Connection timeout
   Retrying in 3 seconds...
   ```
   **Solution**: System automatically retries; check internet connection

3. **JSON Validation Failures**
   ```
   ⚠️ JSON validation failed (attempt 1/3)
   Retrying with error feedback...
   ```
   **Solution**: System provides feedback to AI and retries automatically

### Fallback Behavior

When all validation attempts fail, the system generates schema-compliant default responses to ensure continuity.

## Technical Architecture

### Core Components

- **JSON Schema Validation**: Ensures structured, reliable AI responses
- **Retry Logic**: Handles API failures and validation errors
- **Template System**: Structured prompts for consistent AI behavior
- **Metrics Collection**: Performance monitoring and optimization data

### AI Integration

- **Model**: Claude 3 Opus (high quality) or Sonnet (cost-effective)
- **Prompt Engineering**: Structured templates with schema enforcement
- **Response Parsing**: Robust JSON extraction with markdown cleanup
- **Validation Feedback**: Error-specific retry prompts

## Cost Considerations

- **Claude 3 Opus**: Higher quality, higher cost (~$15/million input tokens)
- **Claude 3 Sonnet**: Balanced quality/cost (~$3/million input tokens)
- **Token Usage**: ~500-1000 tokens per assessment (including retries)
- **Estimated Cost**: $0.01-0.02 per complete assessment

## Educational Applications

### Suitable For

- **Formative Assessment**: Quick comprehension checks
- **Study Aid**: Self-assessment with immediate feedback
- **Educational Research**: Consistent rubric application
- **Teacher Tools**: Rapid question generation for various topics

### Best Practices

- **Clear Topics**: Specific, well-defined subject areas work best
- **Appropriate Scope**: Questions designed for ~100-word responses
- **Subject Variety**: Works across STEM, humanities, and social sciences
- **Quality Review**: Always review AI-generated content for accuracy

## Limitations

- **AI Dependency**: Requires internet connection and API access
- **Subject Expertise**: AI assessment quality varies by topic complexity
- **Response Length**: Optimized for short-form answers (~100 words)
- **Language**: Currently English-only interface and assessment

## Contributing

To enhance the system:

1. **Schema Extension**: Add new validation schemas for different question types
2. **Prompt Optimization**: Improve AI instruction templates
3. **Export Formats**: Add support for additional output formats
4. **Multi-language**: Extend support for non-English assessments

## License

CC0 1.0
 
CC0 1.0 Universal
By marking the work with a CC0 public domain dedication, the creator is giving up their copyright and allowing reusers to distribute, remix, adapt, and build upon the material in any medium or format, even for commercial purposes.

CC0 This work has been marked as dedicated to the public domain.

This is a proof-of-concept educational tool. Ensure compliance with Anthropic's terms of service when using their API.

## Support

For issues or questions:
- Check the error messages for specific guidance
- Verify API key configuration
- Review network connectivity
- Consult Anthropic documentation for API-related issues
