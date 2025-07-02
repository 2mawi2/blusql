from pharia_skill.testing import DevCsi
import time
from generate_query import Input, Output, generate_query
from intelligence_layer.core import NoOpTracer, Task, TaskSpan
from dotenv import load_dotenv

load_dotenv()


class Text2SQLEvaluationTask(Task):
    def __init__(self):
        self.dev_csi = DevCsi().with_studio(project="test-studio")

    def do_run(self, input: Input, task_span: TaskSpan) -> Output:
        start_time = time.time()
        output = generate_query(self.dev_csi, input)
        duration = time.time() - start_time

        return Output(answer=output.answer, duration=duration)


if __name__ == "__main__":

    test_input = Input(natural_query="How many singers do we have?")

    # Initialize task
    task = Text2SQLEvaluationTask()

    # Run the task with dummy span (NoOpTracer just does nothing — good for testing)
    output = task.do_run(test_input, task_span=NoOpTracer())

    # Print the result
    print("\n--- Evaluation Output ---")
    print(f"SQL Query:\n{output.sql_query}\n")
    if output.markdown_result:
        print("Markdown Table:\n", output.markdown_result)
    if output.explanation:
        print("Explanation:\n", output.explanation)
