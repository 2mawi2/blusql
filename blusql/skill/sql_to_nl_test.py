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
        
        if "top 3 customers" in message_content.lower():
            response_content = """Based on your query results, the top 3 customers by total spending are clearly identified. John Smith leads with $5,250, followed by Sarah Wilson at $4,800, and Mike Johnson at $3,950. This shows a significant concentration of revenue among your highest-value customers, with John alone contributing over 15% more than the third-highest spender. You might want to implement retention strategies for these valuable customers and analyze what makes them spend more than others."""
        elif "recent orders" in message_content.lower():
            response_content = """Looking at your recent orders data, there's clear activity across multiple days in December 2024. The order amounts vary significantly from $45 to $320, suggesting diverse customer purchasing behaviors. December 15th shows particularly high activity with two orders. This recent activity indicates healthy customer engagement, and you might want to analyze what drove the higher-value orders to replicate those conditions."""
        else:
            response_content = """Based on the query results shown, the data provides clear answers to your question. The results reveal interesting patterns that could inform business decisions. You can see specific values and trends that help understand the underlying business performance."""
        
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
        user_question="Who are our top 3 customers by total spending?",
        sql_result_markdown="""
        | customer_name | total_spent |
        |---------------|-------------|
        | John Smith    | $5,250      |
        | Sarah Wilson  | $4,800      |
        | Mike Johnson  | $3,950      |
        """
    )
    
    result = sql_to_natural_language(csi, test_input)
    
    assert isinstance(result, Output)
    assert isinstance(result.natural_language_response, str)
    assert len(result.natural_language_response) > 0
    assert "john smith" in result.natural_language_response.lower()


def test_sql_to_natural_language_order_table(csi: StubCsi):
    test_input = Input(
        user_question="What are our recent orders?",
        sql_result_markdown="""
        | order_id | customer_name | order_date | amount |
        |----------|---------------|------------|--------|
        | 1001     | Alice Brown   | 2024-12-15 | $125   |
        | 1002     | Bob Davis     | 2024-12-15 | $320   |
        | 1003     | Carol White   | 2024-12-14 | $89    |
        | 1004     | David Lee     | 2024-12-13 | $45    |
        """
    )
    
    result = sql_to_natural_language(csi, test_input)
    
    assert isinstance(result, Output)
    assert isinstance(result.natural_language_response, str)
    assert len(result.natural_language_response) > 0
    assert "december" in result.natural_language_response.lower()


def test_sql_to_natural_language_mock():
    # Mock CSI for more controlled testing
    mock_csi = Mock()
    mock_response = Mock()
    mock_response.message.content = """Looking at your product inventory, you currently have 8 products in stock. The data shows a good variety across categories - Electronics (3 items), Books (3 items), and Clothing (2 items). Your pricing ranges from $12.99 for books up to $899.99 for the laptop, indicating you serve different market segments. The electronics category represents your highest-value inventory with items like the laptop and smartphone. This diverse product mix gives you good market coverage."""
    
    mock_csi.chat.return_value = mock_response
    
    test_input = Input(
        user_question="What products do we have in our inventory?",
        sql_result_markdown="""
        | product_name | category | price | stock_quantity |
        |-------------|----------|-------|----------------|
        | Laptop Pro  | Electronics | $899.99 | 15 |
        | Novel XYZ   | Books    | $12.99  | 50 |
        | T-Shirt     | Clothing | $25.99  | 30 |
        | Smartphone  | Electronics | $599.99 | 8 |
        """
    )
    
    result = sql_to_natural_language(mock_csi, test_input)
    
    assert isinstance(result, Output)
    assert isinstance(result.natural_language_response, str)
    assert len(result.natural_language_response) > 0
    assert "product" in result.natural_language_response.lower()


def test_sql_to_natural_language_empty_response():
    # Mock CSI with empty response
    mock_csi = Mock()
    mock_response = Mock()
    mock_response.message.content = ""
    
    mock_csi.chat.return_value = mock_response
    
    test_input = Input(
        user_question="What is this data about?",
        sql_result_markdown="| id | value |\n|----| ----- |\n| 1  | test  |"
    )
    
    result = sql_to_natural_language(mock_csi, test_input)
    
    assert isinstance(result, Output)
    assert result.natural_language_response == "I couldn't analyze the table structure for your question."


def test_sql_to_natural_language_none_response():
    # Mock CSI with None response content
    mock_csi = Mock()
    mock_response = Mock()
    mock_response.message.content = None
    
    mock_csi.chat.return_value = mock_response
    
    test_input = Input(
        user_question="What is this data about?", 
        sql_result_markdown="| id | value |\n|----| ----- |\n| 1  | test  |"
    )
    
    result = sql_to_natural_language(mock_csi, test_input)
    
    assert isinstance(result, Output)
    assert result.natural_language_response == "I couldn't analyze the table structure for your question."


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
                    user_question="What user accounts were created recently?",
                    sql_result_markdown="""
                    | user_id | username | email | created_at |
                    |---------|----------|-------|------------|
                    | 101     | john_doe | john@example.com | 2024-12-15 |
                    | 102     | jane_smith | jane@example.com | 2024-12-14 |
                    | 103     | bob_wilson | bob@example.com | 2024-12-13 |
                    """
                )
                
                result = sql_to_natural_language(csi, test_input)
                
                print("Generated response:")
                print(result.natural_language_response)
                
                assert len(result.natural_language_response) > 0
            else:
                pytest.skip("PHARIA_STUDIO_ADDRESS not configured")
        else:
            pytest.skip("Environment file not found")
    except ImportError:
        pytest.skip("python-dotenv not available")


def test_sql_to_nl_with_studio_tracing():
    """
    Test function using DevCsi with PhariaStudio tracing.
    Similar to the pattern shown in the RAG tutorial notebook.
    """
    try:
        from dotenv import load_dotenv
        import os
        
        # Only run if environment is properly configured
        if os.path.exists("../.env"):
            load_dotenv("../.env")
            
            if os.getenv("PHARIA_STUDIO_ADDRESS"):
                csi = DevCsi().with_studio("blusql-sql-to-nl")
                
                # Test with a realistic business question
                test_input = Input(
                    user_question="What are our sales trends by month?",
                    sql_result_markdown="""
                    | month | total_sales | order_count |
                    |-------|-------------|-------------|
                    | 2024-10 | $15,420 | 89 |
                    | 2024-11 | $18,950 | 112 |
                    | 2024-12 | $22,340 | 138 |
                    """
                )
                
                result = sql_to_natural_language(csi, test_input)
                
                print("Studio Tracing Test Result:")
                print(f"Question: {test_input.user_question}")
                print("Generated response:")
                print(result.natural_language_response)
                
                # Basic assertions
                assert len(result.natural_language_response) > 0
                assert "purchase" in result.natural_language_response.lower() or "customer" in result.natural_language_response.lower()
                
                print("✅ Studio tracing test completed successfully!")
                print("Check traces at: https://your-studio-url/traces (project: blusql-sql-to-nl)")
                
            else:
                pytest.skip("PHARIA_STUDIO_ADDRESS not configured")
        else:
            pytest.skip("Environment file not found")
    except ImportError:
        pytest.skip("python-dotenv not available")


def test_sql_to_nl_comprehensive_local():
    """
    Comprehensive local testing function with multiple realistic scenarios.
    This function can be run independently for local development and testing.
    """
    try:
        from dotenv import load_dotenv
        import os
        
        print("=" * 80)
        print("SQL-to-NL Skill Comprehensive Local Testing")
        print("=" * 80)
        
        # Check if environment is configured for tracing
        csi = None
        use_tracing = False
        
        if os.path.exists("../.env"):
            load_dotenv("../.env")
            if os.getenv("PHARIA_STUDIO_ADDRESS") and os.getenv("PHARIA_AI_TOKEN"):
                try:
                    csi = DevCsi().with_studio("blusql-sql-to-nl")
                    use_tracing = True
                    print("✅ Using DevCsi with PhariaStudio tracing")
                except Exception as e:
                    print(f"⚠️  Tracing setup failed: {e}")
                    print("Falling back to mock testing...")
        
        if not use_tracing:
            # Use mock CSI for testing without external dependencies
            csi = Mock()
            mock_response = Mock()
            mock_response.message.content = """Based on your query results, the data shows clear business insights. The numbers reveal important patterns about customer behavior and sales performance. This information can help guide strategic decisions about inventory, marketing, and customer retention strategies."""
            csi.chat.return_value = mock_response
            print("🔧 Using mock CSI for local testing")
        
        print()
        
        # Test Case 1: E-commerce Analysis
        print("📊 TEST CASE 1: E-commerce Customer Analysis")
        print("-" * 50)
        
        input1 = Input(
            user_question="Who are our top 5 customers by revenue?",
            sql_result_markdown="""
            | customer_name | total_revenue | order_count |
            |---------------|---------------|-------------|
            | Alice Johnson | $12,450       | 28          |
            | Bob Martinez  | $9,820        | 19          |
            | Carol Davis   | $8,950        | 22          |
            | David Kim     | $7,630        | 15          |
            | Eva Rodriguez | $6,890        | 18          |
            """
        )
        
        result1 = sql_to_natural_language(csi, input1)
        
        print(f"Question: {input1.user_question}")
        print("Generated response:")
        print(result1.natural_language_response)
        
        # Test Case 2: Inventory Management
        print("\n📦 TEST CASE 2: Inventory Management Analysis")
        print("-" * 50)
        
        input2 = Input(
            user_question="Which products are running low on stock?",
            sql_result_markdown="""
            | product_name | current_stock | reorder_point | status |
            |-------------|---------------|---------------|--------|
            | Wireless Mouse | 3 | 10 | Low Stock |
            | USB Cable | 5 | 15 | Critical |
            | Keyboard Pro | 8 | 12 | Low Stock |
            | Monitor Stand | 2 | 8 | Critical |
            """
        )
        
        result2 = sql_to_natural_language(csi, input2)
        
        print(f"Question: {input2.user_question}")
        print("Generated response:")
        print(result2.natural_language_response)
        
        # Test Case 3: Financial Analysis
        print("\n💰 TEST CASE 3: Financial Performance Analysis")
        print("-" * 50)
        
        input3 = Input(
            user_question="What are our monthly revenue trends?",
            sql_result_markdown="""
            | month | revenue | growth_rate |
            |-------|---------|-------------|
            | 2024-09 | $45,200 | -2.1% |
            | 2024-10 | $47,800 | +5.8% |
            | 2024-11 | $52,100 | +9.0% |
            | 2024-12 | $56,750 | +8.9% |
            """
        )
        
        result3 = sql_to_natural_language(csi, input3)
        
        print(f"Question: {input3.user_question}")
        print("Generated response:")
        print(result3.natural_language_response)
        
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE TESTING COMPLETED")
        print("=" * 80)
        
        if use_tracing:
            print("📈 Check PhariaStudio traces at: https://your-studio-url/traces")
            print("🏷️  Project name: blusql-sql-to-nl")
        else:
            print("💡 To enable tracing, configure PHARIA_STUDIO_ADDRESS and PHARIA_AI_TOKEN in ../.env")
        
        # Return results for programmatic access
        return {
            "test1": result1,
            "test2": result2, 
            "test3": result3,
            "tracing_enabled": use_tracing
        }
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    # Allow running comprehensive test directly
    if len(sys.argv) > 1 and sys.argv[1] == "comprehensive":
        test_sql_to_nl_comprehensive_local()
    else:
        pytest.main([__file__])