import pandas as pd
import json
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import logging
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import csv
from io import StringIO
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_NAME = "finance_advisor"
USER_ID = "default_user"


# Pydantic models
class SpendingCategory(BaseModel):
    category: str = Field(..., description="Expense category name")
    amount: float = Field(..., description="Amount spent in this category (INR)")
    percentage: Optional[float] = Field(None, description="Percentage of total spending")


class SpendingRecommendation(BaseModel):
    category: str = Field(..., description="Category for recommendation")
    recommendation: str = Field(..., description="Recommendation details")
    potential_savings: Optional[float] = Field(None, description="Estimated monthly savings (INR)")


class BudgetAnalysis(BaseModel):
    total_expenses: float = Field(..., description="Total monthly expenses (INR)")
    monthly_income: Optional[float] = Field(None, description="Monthly income (INR)")
    spending_categories: List[SpendingCategory] = Field(..., description="Breakdown of spending by category")
    recommendations: List[SpendingRecommendation] = Field(..., description="Spending recommendations")


class EmergencyFund(BaseModel):
    recommended_amount: float = Field(..., description="Recommended emergency fund size (INR)")
    current_amount: Optional[float] = Field(None, description="Current emergency fund (INR)")
    current_status: str = Field(..., description="Status assessment of emergency fund")


class SavingsRecommendation(BaseModel):
    category: str = Field(..., description="Savings category")
    amount: float = Field(..., description="Recommended monthly amount (INR)")
    rationale: Optional[str] = Field(None, description="Explanation for this recommendation")


class AutomationTechnique(BaseModel):
    name: str = Field(..., description="Name of automation technique")
    description: str = Field(..., description="Details of how to implement")


class SavingsStrategy(BaseModel):
    emergency_fund: EmergencyFund = Field(..., description="Emergency fund recommendation")
    recommendations: List[SavingsRecommendation] = Field(..., description="Savings allocation recommendations")
    automation_techniques: Optional[List[AutomationTechnique]] = Field(None,
                                                                       description="Automation techniques to help save")


class Debt(BaseModel):
    name: str = Field(..., description="Name of debt")
    amount: float = Field(..., description="Current balance (INR)")
    interest_rate: float = Field(..., description="Annual interest rate (%)")
    min_payment: Optional[float] = Field(None, description="Minimum monthly payment (INR)")


class PayoffPlan(BaseModel):
    total_interest: float = Field(..., description="Total interest paid (INR)")
    months_to_payoff: int = Field(..., description="Months until debt-free")
    monthly_payment: Optional[float] = Field(None, description="Recommended monthly payment (INR)")


class PayoffPlans(BaseModel):
    avalanche: PayoffPlan = Field(..., description="Highest interest first method")
    snowball: PayoffPlan = Field(..., description="Smallest balance first method")


class DebtRecommendation(BaseModel):
    title: str = Field(..., description="Title of recommendation")
    description: str = Field(..., description="Details of recommendation")
    impact: Optional[str] = Field(None, description="Expected impact of this action")


class DebtReduction(BaseModel):
    total_debt: float = Field(..., description="Total debt amount (INR)")
    debts: List[Debt] = Field(..., description="List of all debts")
    payoff_plans: PayoffPlans = Field(..., description="Debt payoff strategies")
    recommendations: Optional[List[DebtRecommendation]] = Field(None, description="Recommendations for debt reduction")


load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")


def parse_json_safely(data: str, default_value: Any = None) -> Any:
    try:
        return json.loads(data) if isinstance(data, str) else data
    except json.JSONDecodeError:
        return default_value


def parse_csv_transactions(file_content) -> List[Dict[str, Any]]:
    try:
        df = pd.read_csv(StringIO(file_content.decode('utf-8')))
        required_columns = ['Date', 'Category', 'Amount']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df['Amount'] = df['Amount'].replace('[\₹,]', '', regex=True).astype(float)  # Updated for INR
        category_totals = df.groupby('Category')['Amount'].sum().reset_index()

        transactions = df.to_dict('records')
        return {
            'transactions': transactions,
            'category_totals': category_totals.to_dict('records')
        }
    except Exception as e:
        raise ValueError(f"Error parsing CSV file: {str(e)}")


class FinanceAdvisorSystem:
    def __init__(self):
        self.session_service = InMemorySessionService()

        self.budget_analysis_agent = LlmAgent(
            name="BudgetAnalysisAgent",
            model="gemini-2.0-flash-exp",
            description="Analyzes financial data to categorize spending patterns and recommend budget improvements",
            instruction="""You are a Budget Analysis Agent specialized in reviewing financial transactions and expenses.
You are the first agent in a sequence of three financial advisor agents.

Your tasks:
1. Analyze income, transactions, and expenses in detail
2. Categorize spending into logical groups with clear breakdown
3. Identify spending patterns and trends across categories
4. Suggest specific areas where spending could be reduced with concrete suggestions
5. Provide actionable recommendations with specific, quantified potential savings amounts

Consider:
- Number of dependants when evaluating household expenses
- Typical spending ratios for the income level (housing 30%, food 15%, etc.)
- Essential vs discretionary spending with clear separation
- Seasonal spending patterns if data spans multiple months

For spending categories, include ALL expenses from the user's data, ensure percentages add up to 100%,
and make sure every expense is categorized.

For recommendations:
- Provide at least 3-5 specific, actionable recommendations with estimated savings
- Explain the reasoning behind each recommendation
- Consider the impact on quality of life and long-term financial health
- Suggest specific implementation steps for each recommendation

IMPORTANT: Store your analysis in state['budget_analysis'] for use by subsequent agents.""",
            output_schema=BudgetAnalysis,
            output_key="budget_analysis"
        )

        self.savings_strategy_agent = LlmAgent(
            name="SavingsStrategyAgent",
            model="gemini-2.0-flash-exp",
            description="Recommends optimal savings strategies based on income, expenses, and financial goals",
            instruction="""You are a Savings Strategy Agent specialized in creating personalized savings plans.
You are the second agent in the sequence. READ the budget analysis from state['budget_analysis'] first.

Your tasks:
1. Review the budget analysis results from state['budget_analysis']
2. Recommend comprehensive savings strategies based on the analysis
3. Calculate optimal emergency fund size based on expenses and dependants
4. Suggest appropriate savings allocation across different purposes
5. Recommend practical automation techniques for saving consistently

Consider:
- Risk factors based on job stability and dependants
- Balancing immediate needs with long-term financial health
- Progressive savings rates as discretionary income increases
- Multiple savings goals (emergency, retirement, specific purchases)
- Areas of potential savings identified in the budget analysis

IMPORTANT: Store your strategy in state['savings_strategy'] for use by the Debt Reduction Agent.""",
            output_schema=SavingsStrategy,
            output_key="savings_strategy"
        )

        self.debt_reduction_agent = LlmAgent(
            name="DebtReductionAgent",
            model="gemini-2.0-flash-exp",
            description="Creates optimized debt payoff plans to minimize interest paid and time to debt freedom",
            instruction="""You are a Debt Reduction Agent specialized in creating debt payoff strategies.
You are the final agent in the sequence. READ both state['budget_analysis'] and state['savings_strategy'] first.

Your tasks:
1. Review both budget analysis and savings strategy from the state
2. Analyze debts by interest rate, balance, and minimum payments
3. Create prioritized debt payoff plans (avalanche and snowball methods)
4. Calculate total interest paid and time to debt freedom
5. Suggest debt consolidation or refinancing opportunities
6. Provide specific recommendations to accelerate debt payoff

Consider:
- Cash flow constraints from the budget analysis
- Emergency fund and savings goals from the savings strategy
- Psychological factors (quick wins vs mathematical optimization)
- Credit score impact and improvement opportunities

IMPORTANT: Store your final plan in state['debt_reduction'] and ensure it aligns with the previous analyses.""",
            output_schema=DebtReduction,
            output_key="debt_reduction"
        )

        self.coordinator_agent = SequentialAgent(
            name="FinanceCoordinatorAgent",
            description="Coordinates specialized finance agents to provide comprehensive financial advice",
            sub_agents=[
                self.budget_analysis_agent,
                self.savings_strategy_agent,
                self.debt_reduction_agent
            ]
        )

        self.runner = Runner(
            agent=self.coordinator_agent,
            app_name=APP_NAME,
            session_service=self.session_service
        )

    async def analyze_finances(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        session_id = f"finance_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            initial_state = {
                "monthly_income": financial_data.get("monthly_income", 0),
                "dependants": financial_data.get("dependants", 0),
                "transactions": financial_data.get("transactions", []),
                "manual_expenses": financial_data.get("manual_expenses", {}),
                "debts": financial_data.get("debts", [])
            }

            session = self.session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id,
                state=initial_state
            )

            if session.state.get("transactions"):
                self._preprocess_transactions(session)

            if session.state.get("manual_expenses"):
                self._preprocess_manual_expenses(session)

            default_results = self._create_default_results(financial_data)

            user_content = types.Content(
                role='user',
                parts=[types.Part(text=json.dumps(financial_data))]
            )

            async for event in self.runner.run_async(
                    user_id=USER_ID,
                    session_id=session_id,
                    new_message=user_content
            ):
                if event.is_final_response() and event.author == self.coordinator_agent.name:
                    break

            updated_session = self.session_service.get_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id
            )

            results = {}
            for key in ["budget_analysis", "savings_strategy", "debt_reduction"]:
                value = updated_session.state.get(key)
                results[key] = parse_json_safely(value, default_results[key]) if value else default_results[key]

            return results

        except Exception as e:
            logger.exception(f"Error during finance analysis: {str(e)}")
            raise
        finally:
            self.session_service.delete_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id
            )

    def _preprocess_transactions(self, session):
        transactions = session.state.get("transactions", [])
        if not transactions:
            return

        df = pd.DataFrame(transactions)

        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

        if 'Category' in df.columns and 'Amount' in df.columns:
            category_spending = df.groupby('Category')['Amount'].sum().to_dict()
            session.state["category_spending"] = category_spending
            session.state["total_spending"] = df['Amount'].sum()

    def _preprocess_manual_expenses(self, session):
        manual_expenses = session.state.get("manual_expenses", {})
        if not manual_expenses:
            return

        session.state.update({
            "total_manual_spending": sum(manual_expenses.values()),
            "manual_category_spending": manual_expenses
        })

    def _create_default_results(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        monthly_income = financial_data.get("monthly_income", 50000)  # Default to ₹50,000
        expenses = financial_data.get("manual_expenses", {})

        if not expenses and financial_data.get("transactions"):
            expenses = {}
            for transaction in financial_data["transactions"]:
                category = transaction.get("Category", "Uncategorized")
                amount = transaction.get("Amount", 0)
                expenses[category] = expenses.get(category, 0) + amount

        total_expenses = sum(expenses.values())

        return {
            "budget_analysis": {
                "total_expenses": total_expenses,
                "monthly_income": monthly_income,
                "spending_categories": [
                    {"category": cat, "amount": amt,
                     "percentage": (amt / total_expenses * 100) if total_expenses > 0 else 0}
                    for cat, amt in expenses.items()
                ],
                "recommendations": [
                    {"category": "General", "recommendation": "Consider reviewing your expenses carefully",
                     "potential_savings": total_expenses * 0.1}
                ]
            },
            "savings_strategy": {
                "emergency_fund": {
                    "recommended_amount": total_expenses * 6,
                    "current_amount": 0,
                    "current_status": "Not started"
                },
                "recommendations": [
                    {"category": "Emergency Fund", "amount": total_expenses * 0.1,
                     "rationale": "Build emergency fund first"},
                    {"category": "Retirement", "amount": monthly_income * 0.15, "rationale": "Long-term savings"}
                ],
                "automation_techniques": [
                    {"name": "Automatic Transfer", "description": "Set up automatic transfers on payday"}
                ]
            },
            "debt_reduction": {
                "total_debt": sum(debt.get("amount", 0) for debt in financial_data.get("debts", [])),
                "debts": financial_data.get("debts", []),
                "payoff_plans": {
                    "avalanche": {
                        "total_interest": sum(debt.get("amount", 0) for debt in financial_data.get("debts", [])) * 0.2,
                        "months_to_payoff": 24,
                        "monthly_payment": sum(debt.get("amount", 0) for debt in financial_data.get("debts", [])) / 24
                    },
                    "snowball": {
                        "total_interest": sum(debt.get("amount", 0) for debt in financial_data.get("debts", [])) * 0.25,
                        "months_to_payoff": 24,
                        "monthly_payment": sum(debt.get("amount", 0) for debt in financial_data.get("debts", [])) / 24
                    }
                },
                "recommendations": [
                    {"title": "Increase Payments", "description": "Increase your monthly payments",
                     "impact": "Reduces total interest paid"}
                ]
            }
        }