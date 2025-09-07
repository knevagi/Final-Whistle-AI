# European Football Blog - Crew AI Workflow

A scalable, multi-agent system for automated European football content creation using Crew AI. This system creates high-quality blog articles covering recent results, player news, tactical analysis, and transfer updates across all major European leagues.

## 🚀 Overview

The Crew AI workflow consists of three core agents working sequentially:

1. **European Football Content Strategist** - Researches topics and creates comprehensive outlines
2. **European Football Journalist** - Expands outlines into full football articles
3. **European Football Content Editor** - Reviews, edits, and finalizes content for publication

## 📁 File Structure

```
crew_ai/
├── README.md                 # This documentation file
├── requirements.txt          # Python dependencies
├── crew_workflow.py         # Main workflow implementation
├── crew_config.py           # Configuration and settings
├── example_usage.py         # Usage examples and demonstrations
└── specialized_agents.py    # Examples of extending the system
```

## 🛠️ Installation

1. **Install Python dependencies:**
   ```bash
   cd crew_ai
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the `crew_ai` directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Verify installation:**
   ```bash
   python crew_workflow.py
   ```

## 🔧 Basic Usage

### Simple European Football Article Creation

```python
from crew_workflow import AutonomousSportsBlogCrew

# Initialize the crew
crew = AutonomousSportsBlogCrew()

# Create an article
result = crew.create_article(
    topic="Manchester City's Tactical Masterclass Against Arsenal",
    article_type="match_report",
    target_length="1000-1200 words"
)

print(f"Article created: {result['workflow_status']}")
```

### Custom Configuration

```python
from crew_config import update_config

# Update LLM settings
update_config("llm", {
    "temperature": 0.5,
    "max_tokens": 6000
})

# Create crew with custom settings
crew = AutonomousSportsBlogCrew(model_name="gpt-4o-mini")
```

## 🎯 Agent Roles & Responsibilities

### European Football Content Strategist
- **Goal:** Research and create comprehensive content outlines for European football articles
- **Output:** Detailed outlines with research notes, structure, and recommendations
- **Expertise:** Football analysis, content strategy, league knowledge across Europe

### European Football Journalist
- **Goal:** Transform outlines into engaging, well-researched football articles
- **Output:** Complete blog articles ready for editing
- **Expertise:** Football journalism, storytelling, tactical writing

### European Football Content Editor
- **Goal:** Review, edit, and finalize football articles for publication
- **Output:** Polished, publication-ready content with editorial notes
- **Expertise:** Grammar, style, fact-checking, football accuracy verification

## 🔄 Workflow Process

1. **Planning Phase**
   - Topic research and recent match analysis
   - Content structure development
   - SEO keyword identification
   - Target audience definition

2. **Writing Phase**
   - Outline expansion
   - Content creation with football context
   - Tactical accuracy verification
   - Engaging narrative development

3. **Editing Phase**
   - Grammar and style review
   - Football fact verification
   - SEO optimization
   - Final quality check

## 🚀 Extending the System

### Adding Specialized European Football Agents

The system is designed for easy extension. You can add specialized agents like:

- **Transfer Market Specialist** - Analyzes transfer news and rumors
- **Tactical Analyst** - Provides deep tactical insights
- **Player Performance Analyst** - Tracks player statistics and form
- **Match Statistics Expert** - Analyzes data and metrics
- **European Competition Specialist** - Covers Champions League, Europa League

### Example: Adding a New Football Agent

```python
from crewai import Agent
from specialized_agents import EuropeanFootballAgentFactory

# Create a specialized agent
factory = EuropeanFootballAgentFactory(llm)
transfer_specialist = factory.create_transfer_market_specialist()

# Add to your crew
crew.add_specialized_agent(transfer_specialist, "Transfer Specialist")
```

## ⚙️ Configuration

### LLM Settings
- **Default Model:** GPT-4o-mini
- **Temperature:** 0.7 (configurable)
- **Max Tokens:** 4000 (configurable)
- **Fallback Model:** GPT-3.5-turbo

### Content Types
- **Match Report:** 800-1200 words, exciting and detailed tone
- **Player Analysis:** 1000-1500 words, analytical and insightful tone
- **Transfer News:** 800-1200 words, informative and engaging tone
- **Tactical Analysis:** 1000-1500 words, technical and analytical tone
- **League Roundup:** 1200-1800 words, comprehensive and engaging tone

### Quality Assurance
- **Fact Checking:** Enabled
- **Grammar Checking:** Enabled
- **Football Accuracy Check:** Enabled
- **Readability Target:** 70+ score
- **Minimum Word Count:** 600 words

## 📊 Monitoring & Optimization

### Crew Information
```python
crew_info = crew.get_crew_info()
print(f"Total Agents: {crew_info['total_agents']}")
print(f"Agent Roles: {crew_info['agent_roles']}")
print(f"Process Type: {crew_info['process_type']}")
```

### Performance Metrics
- Article completion time
- Quality scores
- Error rates
- Agent collaboration efficiency

## 🔒 Security & Best Practices

1. **API Key Management**
   - Store API keys in environment variables
   - Never commit keys to version control
   - Use different keys for development/production

2. **Content Validation**
   - Always review AI-generated football content
   - Implement fact-checking processes
   - Maintain editorial oversight

3. **Rate Limiting**
   - Monitor API usage
   - Implement appropriate delays
   - Use fallback models when needed

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify `.env` file exists
   - Check API key validity
   - Ensure proper file permissions

2. **Import Errors**
   - Verify all dependencies are installed
   - Check Python path configuration
   - Ensure files are in correct directories

3. **Content Quality Issues**
   - Adjust temperature settings
   - Review agent backstories
   - Modify task descriptions

### Debug Mode

Enable verbose logging:
```python
crew = AutonomousSportsBlogCrew()
crew.crew.verbose = True
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **Agent Pool:** Up to 10 concurrent agents
- **Load Balancing:** Automatic distribution of tasks
- **Fallback Agents:** Redundant agent availability

### Vertical Scaling
- **Model Upgrades:** Switch to more powerful LLMs
- **Memory Enhancement:** Add persistent memory systems
- **Task Complexity:** Increase task granularity

## 🤝 Contributing

To extend or improve the system:

1. **Fork the repository**
2. **Create a feature branch**
3. **Implement your changes**
4. **Add tests and documentation**
5. **Submit a pull request**

## 📚 Additional Resources

- [Crew AI Documentation](https://docs.crewai.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:

1. Check the troubleshooting section
2. Review example usage files
3. Examine configuration options
4. Create an issue in the repository

---

**Happy Football Content Creating! ⚽📝**
