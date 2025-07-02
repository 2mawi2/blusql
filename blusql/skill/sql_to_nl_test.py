import pytest
from unittest.mock import Mock
from pharia_skill.testing import DevCsi, StubCsi
from pharia_skill import (
    Message,
    ChatParams,
    ChatResponse,
    Role,
    FinishReason,
    TokenUsage,
)

from sql_to_nl import Input, Output, sql_to_natural_language


class CustomStubCsi(StubCsi):
    def chat(
        self, model: str, messages: list[Message], params: ChatParams
    ) -> ChatResponse:
        # Simulate different responses based on input content
        message_content = messages[0].content if messages else ""
        
        if "how many customers" in message_content.lower():
            response_content = """1. Based on the table structure, you would count rows in the Customers table to answer this question
2. The table has a CustomerID as primary key, so each row represents one unique customer
3. The table contains customer contact information including names, emails, and phone numbers
4. The created_at timestamp field shows when each customer registered"""
        elif "who are the top customers" in message_content.lower():
            response_content = """1. This question requires joining the Orders table with Customers table to calculate customer rankings
2. The customer_id foreign key links customers to their orders for aggregation
3. You could rank customers by total_amount, number of orders, or order frequency
4. The order_date field allows for time-based customer analysis"""
        else:
            response_content = """1. The question can be answered by analyzing the provided table structure
2. The table contains relevant fields that relate to your query
3. Additional insights depend on the specific relationships shown in the schema"""
        
        return ChatResponse(
            message=Message(
                role=Role.Assistant,
                content=response_content,
            ),
            finish_reason=FinishReason.STOP,
            logprobs=[],
            usage=TokenUsage(prompt=0, completion=0),
        )


@pytest.fixture
def csi() -> StubCsi:
    return CustomStubCsi()


def test_sql_to_natural_language_customer_table(csi: StubCsi):
    test_input = Input(
        user_question="How many customers do we have?",
        sql_table_markdown="""
        | Column | Type | Description |
        |--------|------|-------------|
        | id | INT | Primary key |
        | name | VARCHAR(100) | Customer name |
        | email | VARCHAR(255) | Customer email |
        | phone | VARCHAR(20) | Phone number |
        | created_at | TIMESTAMP | Registration date |
        """
    )
    
    result = sql_to_natural_language(csi, test_input)
    
    assert isinstance(result, Output)
    assert isinstance(result.natural_language_expressions, list)
    assert len(result.natural_language_expressions) == 4
    assert "count rows" in result.natural_language_expressions[0].lower()


def test_sql_to_natural_language_order_table(csi: StubCsi):
    test_input = Input(
        user_question="Who are the top customers by spending?",
        sql_table_markdown="""
        | Column | Type | Constraints | Description |
        |--------|------|-------------|-------------|
        | order_id | INT | PRIMARY KEY | Order identifier |
        | customer_id | INT | FOREIGN KEY | References customer table |
        | order_date | DATE | NOT NULL | When order was placed |
        | status | ENUM | DEFAULT 'pending' | Order status |
        | total_amount | DECIMAL(12,2) | NOT NULL | Total order value |
        """
    )
    
    result = sql_to_natural_language(csi, test_input)
    
    assert isinstance(result, Output)
    assert len(result.natural_language_expressions) == 4
    assert "joining" in result.natural_language_expressions[0].lower()


def test_sql_to_natural_language_mock():
    # Mock CSI for more controlled testing
    mock_csi = Mock()
    mock_response = Mock()
    mock_response.message.content = """1. Product catalog table for inventory management
2. Contains product details and pricing information
3. Tracks stock levels and product categories
4. Enables analysis of product performance metrics
5. Supports inventory optimization decisions"""
    
    mock_csi.chat.return_value = mock_response
    
    test_input = Input(
        user_question="What products do we sell?",
        sql_table_markdown="""
        | Column | Type | Description |
        |--------|------|-------------|
        | product_id | INT | Product identifier |
        | name | VARCHAR(200) | Product name |
        | price | DECIMAL(10,2) | Product price |
        """
    )
    
    result = sql_to_natural_language(mock_csi, test_input)
    
    assert isinstance(result, Output)
    assert len(result.natural_language_expressions) == 5
    assert "Product catalog table" in result.natural_language_expressions[0]


def test_sql_to_natural_language_empty_response():
    # Mock CSI with empty response
    mock_csi = Mock()
    mock_response = Mock()
    mock_response.message.content = ""
    
    mock_csi.chat.return_value = mock_response
    
    test_input = Input(
        user_question="What is this table for?",
        sql_table_markdown="| id | INT | Primary key |"
    )
    
    result = sql_to_natural_language(mock_csi, test_input)
    
    assert isinstance(result, Output)
    assert result.natural_language_expressions == []


def test_sql_to_natural_language_none_response():
    # Mock CSI with None response content
    mock_csi = Mock()
    mock_response = Mock()
    mock_response.message.content = None
    
    mock_csi.chat.return_value = mock_response
    
    test_input = Input(
        user_question="What is this table for?", 
        sql_table_markdown="| id | INT | Primary key |"
    )
    
    result = sql_to_natural_language(mock_csi, test_input)
    
    assert isinstance(result, Output)
    assert result.natural_language_expressions == []


def test_sql_to_natural_language_with_tracing():
    """Test function that can be used with tracing enabled when environment is configured"""
    try:
        from dotenv import load_dotenv
        import os
        
        # Only run if environment is properly configured
        if os.path.exists("../.env"):
            load_dotenv("../.env")
            
            if os.getenv("PHARIA_STUDIO_ADDRESS"):
                csi = DevCsi().with_studio("blusql-sql-to-nl")
                
                test_input = Input(
                    user_question="How can I find user account details?",
                    sql_table_markdown="""
                    | Column | Type | Constraints | Description |
                    |--------|------|-------------|-------------|
                    | user_id | INT | PRIMARY KEY | User identifier |
                    | username | VARCHAR(50) | UNIQUE | User login name |
                    | email | VARCHAR(255) | NOT NULL | User email address |
                    | created_at | TIMESTAMP | DEFAULT NOW() | Account creation time |
                    """
                )
                
                result = sql_to_natural_language(csi, test_input)
                
                print("Generated expressions:")
                for i, expr in enumerate(result.natural_language_expressions, 1):
                    print(f"{i}. {expr}")
                
                assert len(result.natural_language_expressions) > 0
            else:
                pytest.skip("PHARIA_STUDIO_ADDRESS not configured")
        else:
            pytest.skip("Environment file not found")
    except ImportError:
        pytest.skip("python-dotenv not available")


if __name__ == "__main__":
    pytest.main([__file__])