from langchain.agents import create_agent
from langchain_openai import ChatOpenAI 
from src.config import settings 
from src.schemas import EvaluationLLMOut, AgentResponse, EvaluateToolInput, UpdateToolInput, UpdateLLMOut
from langchain.tools import tool
from langchain.messages import HumanMessage
from src.config import settings

class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.openrouter_url,
            api_key=settings.openrouter_api_key,
            model=settings.llm, 
            temperature=0,
            max_completion_tokens=500,
        )
        # Define tool inside the constructor (so it can access self.llm and there's no error with @tool decorator)
        @tool("evaluate_prompt", args_schema=EvaluateToolInput)
        def evaluate_prompt(prompt_content: str, 
                            query: str, 
                            rag_ans: str, 
                            correct_answer: str,
                            context: str) -> str:
                """
                Evaluates the quality of a RAG-generated answer against a user query, a gold (correct) answer, and the provided context.

                Input Arguments:
                - prompt_content (str): The instruction or prompt used to generate the RAG answer.
                - query (str): The original user question.
                - rag_ans (str): The answer produced by the RAG system.
                - correct_answer (str): The expected or gold-standard answer.
                - context (str): The retrieved or supporting context provided to the RAG system.

                Evaluation Metrics:
                - Faithfulness (0–1): Measures whether the RAG answer strictly adheres to the given context
                without hallucinations or unsupported claims.
                - Context Relevancy (0–1): Measures how relevant the provided context is for answering the query.
                - Answer Relevancy (0–1): Measures how well the RAG answer addresses the user query
                compared to the correct answer.

                Expected Response:
                - Return a structured output containing the context provided to the tool, evaluation scores for each metric, and reason and quality. The structured output should look like:
                {
                         "prompt_content": prompt_content,    
                         "query:" : query,
                         "rag_ans": rag_ans,
                         "correct_answer": correct_answer,
                         "context": context,
                         "faithfulness": scores.faithfulness,  
                         "context_relevancy": scores.context_relevancy,
                         "answer_relevancy": scores.answer_relevancy,
                         "quality": "fail",                  
                         "reason": reason
                }
                """

                evaluation_prompt = f"""
                You are an expert RAG evaluation model.

                Your task is to evaluate the quality of a Retrieval-Augmented Generation (RAG)
                answer using three metrics: Faithfulness, Context Relevancy, and Answer Relevancy.

                You are given the following inputs:

                ---
                Prompt Content: {prompt_content}
                User Query: {query}
                RAG Answer: {rag_ans}
                Correct Answer (Gold Standard): {correct_answer}
                Provided Context: {context}
                ---

                ### Evaluation Guidelines

                You MUST output numeric scores between 0.0 and 1.0 for each metric.

                #### 1. Faithfulness
                Score how strictly the RAG Answer is grounded in the Provided Context.
                - 1.0 → All claims are directly supported by the context.
                - 0.5 → Some claims are implied but not clearly stated.
                - 0.0 → Contains hallucinations or unsupported information.

                Do NOT use outside knowledge.

                #### 2. Context Relevancy
                Score how useful and relevant the Provided Context is for answering the User Query.
                - 1.0 → Context directly supports answering the query.
                - 0.5 → Context is partially relevant or incomplete.
                - 0.0 → Context is irrelevant.

                Judge the context itself, not the answer.

                #### 3. Answer Relevancy
                Score how well the RAG Answer addresses the User Query compared to the Correct Answer.
                - 1.0 → Fully answers the query correctly and clearly.
                - 0.5 → Partially answers or misses key details.
                - 0.0 → Incorrect or unrelated answer.

                #### 4. Reason:
                Provide a short and concise one line explanation for a particular low score.

                ### Output Rules
                - Return ONLY structured output matching the EvaluationLLMOut schema.
                """
                faithfulness_thres = 0.7
                conext_relevancy_thres = 0.7
                answer_relevancy_thres = 0.7 

                # Get structured output for evaluation scores
                evaluator = self.llm.with_structured_output(EvaluationLLMOut)
                scores = evaluator.invoke(evaluation_prompt)
                reason = scores.reason
                
                # Compare with thresholds to determine pass/fail
                if (scores.faithfulness >= faithfulness_thres and
                    scores.context_relevancy >= conext_relevancy_thres and
                    scores.answer_relevancy >= answer_relevancy_thres):
                    return {
                         "prompt_id": prompt_content,     # CONTEXT
                         "query:" : query,
                    }
                else:
                    return {
                         "prompt_content": prompt_content,     # CONTEXT
                         "query:" : query,
                         "rag_ans": rag_ans,
                         "correct_answer": correct_answer,
                         "context": context,
                         "faithfulness": scores.faithfulness,  # EVALUATION SCORES
                         "context_relevancy": scores.context_relevancy,
                         "answer_relevancy": scores.answer_relevancy,
                         "quality": "fail",                    # FINAL QUALITY 
                         "reason": reason
                    }
                
        @tool("update_prompt", args_schema=UpdateToolInput)
        def update_prompt(prompt_content: str, 
                          query: str, 
                          rag_ans: str, 
                          correct_answer: str,
                          context: str,
                          faithfulness: float,
                          context_relevancy: float,
                          answer_relevancy: float,
                          quality: str,
                          reason: str,
                          ) -> str:
                """
                Updates the prompt content if the quality from evaluate_prompt is "fail".

                Input Arguments:
                - prompt_content (str): The instruction or prompt used to generate the RAG answer.
                - query (str): The original user question.
                - rag_ans (str): The answer produced by the RAG system.
                - correct_answer (str): The expected or gold-standard answer.
                - context (str): The retrieved or supporting context provided to the RAG system.
                - faithfulness (float): Score how strictly the RAG Answer is grounded in the Provided Context.
                - context_relevancy (float): Score how useful and relevant the Provided Context is for answering the User Query.
                - answer_relevancy (float): Score how well the RAG Answer addresses the User Query compared to the Correct Answer.
                - quality (str): Overall quality evaluation result ("pass" or "fail").
                - reason (str): One line explanation for a particular low score.

                Expected Response:
                - Returns a structured output containing the prompt id, fixed or existing prompt based on the quality. The structured output should look like:
                {
                    "quality": quality ("pass" or "fail"),
                    "prompt_content": updated_prompt(if quality is "fail", else existing prompt)
                    "reason": reason (one line explanation for a low score)
                }
                """
                if quality == "pass":
                     return {
                          "quality": "pass",
                          "prompt_content": prompt_content,
                          "reason": reason
                     }
                
                updater_prompt = f"""You are an expert prompt engineer responsible for refining prompt instructions used in a Retrieval-Augmented Generation (RAG) system.
                Your sole task is to update the prompt content based strictly on the provided inputs.

                You MUST return your response strictly in the UpdateLLMOut structured format.
                DO NOT include any extra text, explanations, markdown, or commentary outside the structured output.

                ### INPUTS

                Current Prompt: {prompt_content}
                User Query: {query}
                RAG Answer: {rag_ans}
                Correct Answer: {correct_answer}
                Retrieved Context: {context}

                Evaluation Signals (for guidance only):
                - Faithfulness Score: {faithfulness}
                - Context Relevancy Score: {context_relevancy}
                - Answer Relevancy Score: {answer_relevancy}
                - Quality Result: {quality}
                - Reason for assigning the scores: {reason}

                ### IMPORTANT: YOUR TASK
                - Update the prompt based on the given User Query, Retrieved Context, RAG Answer, Correct Answer.
                - Look at the Evaluation Signals for guidance on what to improve in the Current Prompt.
                - Preserve the original intent of the Current Prompt unless it directly caused the failure.

                The updated prompt should be written as a standalone instruction for a generation model.

                ### IMPORTANT: PROMPT UPDATE RULES
                - Output a COMPLETE, production-ready prompt.
                - Do NOT reference: evaluation scores, "RAG answer", "correct answer", internal analysis or reasoning steps.

                ### OUTPUT FORMAT: STRICTLY ADHERE TO THIS SCHEMA
                {UpdateLLMOut}

                Any deviation from this format will be treated as an invalid response.
                """ 

                updater = self.llm.with_structured_output(UpdateLLMOut)
                updated_prompt = updater.invoke(updater_prompt)
                return {
                     "quality": "fail",
                     "prompt_content": updated_prompt.updated_prompt,
                     "reason": reason
                }
        self.tools = [evaluate_prompt, update_prompt]

        # Define system prompt for the agent
        self.prompt = """
        You are an evaluation agent responsible for assessing RAG answer quality and finally updating prompts when necessary.
        You've two specialized tools at your disposal: `evaluate_prompt` and `update_prompt`.

        ### Core Responsibilities
        - Provide the input to the evaluate_prompt tool to assess RAG answer quality.
        - Use the update_prompt tool to refine the prompt.
        - Produce a final structured response using the AgentResponse schema.

        ### Tool Usage Rules
        - Always call the `evaluate_prompt` tool when the user provides:
        prompt_content, query, rag_ans, correct_answer, and context.
        - Pass the output from `evaluate_prompt` to the `update_prompt` tool
        - Based on the response from `update_prompt`, produce the final response strictly following the AgentResponse schema.

        ### Decision Logic
        - Rely exclusively on the tool's returned result to provide the final output.

        ### Response Handling
        - Always return a structured AgentResponse.
        - The response fields must be the output from the last tool called (update_prompt).
        - Agent Response schema:
        {
            "quality": ,
            "prompt_content": ,
            "reason": ""
        }
        - Do not alter the tool's output before providing the final response.

        You are optimized for correctness, consistency, and efficient tool orchestration.
        """

        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.prompt,
            response_format=AgentResponse
        )

    # Evaluation method 
    def evaluate(self, prompt_content: str, query: str, rag_ans: str, correct_answer: str, context: str) -> str:
        human_message = HumanMessage(
            content=f"""Evaluate the prompt with the following details:
            Prompt Content: {prompt_content}
            Query: {query}
            RAG Answer: {rag_ans}
            Correct Answer: {correct_answer}
            Context: {context}"""
        )
        for step in self.agent.stream({"messages": [human_message]},
                                      stream_mode="values"):
            step["messages"][-1].pretty_print()  # for debugging
        final_response = step["messages"][-1].content  
        return final_response
      
agent = EvaluatorAgent()

# # ------ TESTING AGENT -----
# resp=agent.evaluate(prompt_content="Provide a good response to the query based on the context.",
#                query="How can I book a hotel room?",
#                rag_ans="You need to call the hotel directly to make a reservation. Online booking is not available.",
#                correct_answer="You can book a hotel room through our website by selecting your destination, dates, and preferred room type, then completing the payment process. ",
#                context="Our booking platform allows users to search for hotels by destination and dates. The system displays available rooms with pricing, amenities, and photos. Users can filter results by price, rating, and facilities. Once a room is selected, guests enter their details and payment information to complete the reservation. The entire process is secure and typically takes 5-10 minutes.")
