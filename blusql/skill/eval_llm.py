from pharia_skill.testing import DevCsi
import time
from generate_query import Input, Output, generate_query, DbContext
from intelligence_layer.core import NoOpTracer, Task, TaskSpan
from dotenv import load_dotenv
from env_generate_examples import generate_examples
import logging
from pharia_skill.testing import DevCsi
from pydantic import BaseModel
import os
from intelligence_layer.connectors import StudioClient
from intelligence_layer.evaluation import (
    Example,
    StudioDatasetRepository,
    StudioBenchmarkRepository,
)
from eval_metrics import QaEvaluationLogic, QaAggregationLogic, QaEvaluation


load_dotenv()

PROJECT_NAME = "bluesql"


class Text2SQLEvaluationTask(Task):
    def __init__(self):
        self.dev_csi = DevCsi().with_studio(project=PROJECT_NAME)

    def do_run(self, input: Input, task_span: TaskSpan) -> Output:
        start_time = time.time()
        output = generate_query(self.dev_csi, input)
        duration = time.time() - start_time

        return output


studio_client = StudioClient(
    project=PROJECT_NAME,
    studio_url=os.getenv("PHARIA_STUDIO_ADDRESS"),
    auth_token=os.getenv("PHARIA_AI_TOKEN"),
    create_project=True,
)


class ExpectedOutput(BaseModel):
    sql_query: str


studio_dataset_repo = StudioDatasetRepository(studio_client=studio_client)
studio_benchmark_repo = StudioBenchmarkRepository(studio_client=studio_client)


examples = [
    Example(
        input=example["question"],
        expected_output=example["query"],
        metadata={"db_id": example["db_id"]},
    )
    for example in generate_examples()
]


# studio_dataset = studio_dataset_repo.create_dataset(
#    examples=examples, dataset_name="test-dataset"
# )

# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
# )


if __name__ == "__main__":
    task = Text2SQLEvaluationTask()
    eval_logic = QaEvaluationLogic()
    aggregator = QaAggregationLogic()

    all_evaluations = []
    # benchmark = studio_benchmark_repository.create_benchmark(dataset.id, evaluation_logic, aggregation_logic)

    for example_data in generate_examples():
        # --- Build input and expected output
        test_input = Input(
            natural_query=example_data["question"],
            db_context=example_data["db_context"],
        )

        expected_output = ExpectedOutput(sql_query=example_data["query"])

        example = Example(input=test_input, expected_output=expected_output)

        # --- Run actual system
        output: Output = task.do_run(test_input, task_span=NoOpTracer())

        # --- Evaluate
        evaluation: QaEvaluation = eval_logic.do_evaluate_single_output(example, output)

        all_evaluations.append(evaluation)

        # --- Print output + scores
        print("\n--- Evaluation Output ---")
        print(f"Natural Query: {test_input.natural_query}")
        print(f"Generated SQL: {output.sql_query}")
        print(f"Expected SQL:\n{expected_output.sql_query}")
        # print(f"Generated Markdown:\n{output.markdown_result}")
        print("\n--- LLM-as-a-Judge Scores ---")
        print(f"Accuracy: {evaluation.accuracy_score}")
        print(f"Factuality: {evaluation.factuality_score}")
        print(f"Completeness: {evaluation.completeness_score}")
        print(f"Levenshtein Score: {evaluation.levenshtein_score}")

        # Run only first example
        # break

        # --- Aggregate scores across all evaluated examples
    aggregated_scores = aggregator.aggregate(all_evaluations)

    print("\n=== Aggregated Evaluation Scores ===")
    print(f"Average Accuracy: {aggregated_scores.average_accuracy_score}")
    print(f"Average Factuality: {aggregated_scores.average_factuality_score}")
    print(f"Average Completeness: {aggregated_scores.average_completeness_score}")
    print(f"Average Levenshtein Score: {aggregated_scores.average_levenshtein_score}")
