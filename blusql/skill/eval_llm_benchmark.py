from pharia_skill.testing import DevCsi
import time
from generate_query import Input, Output, generate_query
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


class Text2SQLEvaluationTask(Task[Input, Output]):
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


studio_dataset_repo = StudioDatasetRepository(studio_client=studio_client)
studio_benchmark_repo = StudioBenchmarkRepository(studio_client=studio_client)


examples = [
    Example(
        input=Input(natural_query=example["question"], db_context=example["db_context"]),
        expected_output=example["query"],
        metadata={"db_id": example["db_id"]},
    )
    for example in generate_examples()
]

# studio_dataset = studio_dataset_repo.create_dataset(
#    examples=examples, dataset_name="test-dataset"
# )

studio_dataset_id = "70bca9c3-6ceb-4b83-a302-f081cf87dfb8"

eval_logic = QaEvaluationLogic()
aggregator = QaAggregationLogic()

# benchmark = studio_benchmark_repo.create_benchmark(
#     dataset_id=studio_dataset_id,
#     eval_logic=eval_logic,
#     aggregation_logic=aggregator,
#     name="bluesql-eval",
# )

benchmark = studio_benchmark_repo.get_benchmark("0f96a69c-03c2-4c68-90b0-5c22053abaf9", eval_logic, aggregator)

task = Text2SQLEvaluationTask()
benchmark.execute(task, "bluesql-eval-task")
