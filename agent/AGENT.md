# EduPilot: AI Academic Decision Agent for College Students

## Use case

- **Pitch:** An AI study coach that helps students choose what to study next—by assessing topics, building study plans, recording quiz results, and adapting recommendations in real time.

- **Who it is for:** College students with multiple subjects, variable topic mastery, uneven exam schedules, and limited study hours who need to optimize their preparation.

- **Example interaction:**
  - Student: "I have an exam on Thermodynamics in 5 days and Electronics in 2 weeks. I'm strong in circuits but weak in heat transfer. What should I study next?"
  - EduPilot: "Quiz on heat transfer first—it's weak and closer. I'll create a 5-day plan. Want to assess heat transfer fundamentals first?"

- **Features:**
  - **Topic assessment:** ask students about their understanding and recent practice; record their answers.
  - **Study plan generation:** build realistic plans based on exam dates, topic strength, and available hours.
  - **Quiz recording:** capture quiz scores and adjust the plan based on results.
  - **Adaptive replanning:** respond to changes (new exam date, topic weakness discovered).
  - **Natural explanations:** why a topic is urgent, what the plan covers, and what comes next.
  - **Live decision panel:** see which academic action the model chose and why.
  - **Deployed on Amazon Bedrock AgentCore Runtime.**

- **The decision handed to Strands Decider 2B:** what academic action should the agent take next—assess, plan, record, replan, explain, or ask for clarification? (`#tool-selection`)

- **Why a decision model:** the agent must pick the right tool for each request, based on the student's words and study state (subjects, exams, quiz history, current plan). Strands Decider 2B reads language and context better than arithmetic, and the decision is fast and private.

- **Amazon Bedrock:** powers the conversation, tool calling, and planning logic. Local Ollama runs during development, hosted LLM through AWS UG Madurai cloud.

