from langchain.agents import create_agent
from langchain_openai import ChatOpenAI 
from src.config import settings 
from src.schemas import EvaluationLLMOut, EvaluateToolInput
from langchain.tools import tool
from langchain.messages import HumanMessage
from src.config import settings
import json

from langchain_openai import ChatOpenAI

class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.llm,   
            temperature=0,
        )

        self.eval_llm = ChatOpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.llm,   
            temperature=0,
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
                Use this tool when you need to evaluate RAG answer quality."""

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
                context_relevancy_thres = 0.7
                answer_relevancy_thres = 0.7 

                # Get structured output for evaluation scores
                # try:
                evaluator = self.eval_llm.with_structured_output(EvaluationLLMOut)
                scores = evaluator.invoke(evaluation_prompt)
                reason = scores.reason
                # except Exception as e:
                #     return json.dumps({
                #          "faithfulness": 0.0,
                #          "context_relevancy": 0.0,
                #          "answer_relevancy": 0.0,
                #          "quality": "fail",
                #          "reason": f"Error during evaluation: {str(e)}"
                #     })
                    
                # Compare with thresholds to determine pass/fail
                if (scores.faithfulness >= faithfulness_thres and
                    scores.context_relevancy >= context_relevancy_thres and
                    scores.answer_relevancy >= answer_relevancy_thres):
                    return json.dumps({
                         "faithfulness": scores.faithfulness,  # EVALUATION SCORES
                         "context_relevancy": scores.context_relevancy,
                         "answer_relevancy": scores.answer_relevancy,
                         "quality": "pass",                    # FINAL QUALITY 
                         "reason": reason
                    })
                else:
                    return json.dumps({
                         "faithfulness": scores.faithfulness,  # EVALUATION SCORES
                         "context_relevancy": scores.context_relevancy,
                         "answer_relevancy": scores.answer_relevancy,
                         "quality": "fail",                    # FINAL QUALITY 
                         "reason": reason
                    })
                
      
        self.tools = [evaluate_prompt]

        # Define system prompt for the agent
        self.prompt = """
        You are an evaluation agent responsible for assessing RAG answer quality.
        You've a specialized tool at your disposal: `evaluate_prompt`.

        ### Core Responsibilities
        - Provide the input to the evaluate_prompt tool to assess RAG answer quality.
        - Produce a final structured response using the AgentResponse schema.

        ### Tool Usage Rules
        - Always call the `evaluate_prompt` tool when the user provides:
        prompt_content, query, rag_ans, correct_answer, and context.

        ### Decision Logic
        - Rely exclusively on the tool's returned result to provide the final output.

        ### Response Handling
        - Do not alter the tool's output before providing the final response.

        You are optimized for correctness, consistency, and efficient tool orchestration.
        """

        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.prompt,
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
                print(f"{step=}")
                step["messages"][-1].pretty_print()  # for debugging
                final_response = step["messages"][-1].content       
        return final_response
      
agent = EvaluatorAgent()

# ------ TESTING AGENT -----
resp=agent.evaluate(prompt_content="Provide a good response to the query based on the context.",
               query="How can I book a hotel room?",
               rag_ans="You need to call the hotel directly to make a reservation. Online booking is not available.",
               correct_answer="You can book a hotel room through our website by selecting your destination, dates, and preferred room type, then completing the payment process. ",
               context="Our booking platform allows users to search for hotels by destination and dates. The system displays available rooms with pricing, amenities, and photos. Users can filter results by price, rating, and facilities. Once a room is selected, guests enter their details and payment information to complete the reservation. The entire process is secure and typically takes 5-10 minutes.")

